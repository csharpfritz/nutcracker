using System.Collections.Concurrent;

namespace Nutcracker.Services;

/// <summary>
/// Service to manage and play lightshows
/// </summary>
/// <param name="ledService">The LED service used to control the lights</param>
/// <param name="logger">Logger for logging information</param>
public class LightshowService(LedService ledService, ILogger<LightshowService> logger) : BackgroundService
{
	public event EventHandler? LightshowStarted;
	public event EventHandler? LightshowEnded;
	public event EventHandler? QueueChanged;

	public ConcurrentQueue<LightshowSettings> LightshowQueue { get; } = new();

	public LightshowSettings? CurrentLightshow { get; private set; } = null!;

	public void EnqueueLightshow(LightshowSettings lightshow)
	{
		LightshowQueue.Enqueue(lightshow);
		QueueChanged?.Invoke(this, EventArgs.Empty);
	}

	public static readonly LightshowSettings[] AvailableLightshows =
	[
		new("Santa Claus Is Comin To Town", new TimeSpan(0, 4, 28), "wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3", "wwwroot/lights/santa-claus-is-comin-to-town.json"),
		new("Deck the Halls", new TimeSpan(0, 1, 14), "wwwroot/music/deck-the-halls-christmas-bells-129141.mp3", "wwwroot/lights/deck-the-halls.json"),
		new("Grandma Got Run Over By A Reindeer", new TimeSpan(0, 3, 24), "wwwroot/music/Elmo & Patsy - Grandma Got Run Over By A Reindeer.mp3", "wwwroot/lights/grandma-got-run-over.json"),
		new("Rudolph the Red-Nosed Reindeer", new TimeSpan(0, 3, 8), "wwwroot/music/Gene Autry - Rudolph the Red-Nosed Reindeer (Audio).mp3", "wwwroot/lights/rudolph.json"),
		new("Hark the Herald Angels Sing", new TimeSpan(0, 4, 41), "wwwroot/music/hark-the-herald-angels-sing-celtic-christmas-411990.mp3", "wwwroot/lights/hark-the-herald.json"),
		new("Joy to the World", new TimeSpan(0, 2, 3), "wwwroot/music/joy-to-the-world-xmas-house-background-music-for-video-full-version-431806.mp3", "wwwroot/lights/joy-to-the-world.json"),
		new("O Come All Ye Faithful", new TimeSpan(0, 5, 22), "wwwroot/music/o-come-all-ye-faithful-celtic-christmas-411995.mp3", "wwwroot/lights/o-come-all-ye-faithful.json"),
		new("Oh Christmas Tree", new TimeSpan(0, 1, 41), "wwwroot/music/oh-christmas-tree-168949.mp3", "wwwroot/lights/oh-christmas-tree.json"),
		new("Santa Claus Is Coming to Town (Piano)", new TimeSpan(0, 1, 49), "wwwroot/music/santa-claus-is-coming-to-town-christmas-piano-248543.mp3", "wwwroot/lights/santa-claus-piano.json"),
		new("Silent Night", new TimeSpan(0, 2, 51), "wwwroot/music/silent-night-acoustic-indie-version-127052.mp3", "wwwroot/lights/silent-night.json"),
		new("Wizards in Winter", new TimeSpan(0, 3, 5), "wwwroot/music/trans-siberian-orchestra-wizards-in-winter.mp3", "wwwroot/lights/wizards-in-winter.json")
	];

	// Implementation of the LightshowService
	protected override Task ExecuteAsync(CancellationToken stoppingToken) =>  PlaylightShows(stoppingToken);

	private async Task PlaylightShows(CancellationToken stoppingToken)
	{

		while (!stoppingToken.IsCancellationRequested)
		{
			if (LightshowQueue.TryDequeue(out var lightshowSettings))
			{
				logger.LogInformation($"Starting lightshow: {lightshowSettings.Name}");
				CurrentLightshow = lightshowSettings;
				QueueChanged?.Invoke(this, EventArgs.Empty);
				LightshowStarted?.Invoke(this, EventArgs.Empty);

				try
				{
					// Start playing the music using mplayer
					var musicProcess = new System.Diagnostics.Process
					{
						StartInfo = new System.Diagnostics.ProcessStartInfo
						{
							FileName = "mplayer",
							Arguments = $"\"{lightshowSettings.MusicFilePath}\"",
							UseShellExecute = false,
							CreateNoWindow = true,
							RedirectStandardOutput = true,
							RedirectStandardError = true
						}
					};
					
					musicProcess.Start();
					logger.LogInformation($"Started music playback for: {lightshowSettings.Name}");

					// Start the LED light show in parallel
					var ledTask = Task.Run(async () =>
					{
						await ledService.PlayLedPattern(lightshowSettings, stoppingToken);
					}, stoppingToken);

					// Wait for the music to finish (use duration as max wait time)
					var musicTask = Task.Run(async () =>
					{
						await musicProcess.WaitForExitAsync(stoppingToken);
					}, stoppingToken);

					// Wait for both tasks to complete or use the duration as a timeout
					await Task.WhenAny(
						Task.WhenAll(musicTask, ledTask),
						Task.Delay(lightshowSettings.Duration.Add(TimeSpan.FromSeconds(2)), stoppingToken)
					);

					// Ensure the process is stopped
					if (!musicProcess.HasExited)
					{
						musicProcess.Kill();
					}

					logger.LogInformation($"Finished lightshow: {lightshowSettings.Name}");
				}
				catch (Exception ex)
				{
					logger.LogError(ex, $"Error playing lightshow: {lightshowSettings.Name}");
				}
				finally
				{
					CurrentLightshow = null;
					LightshowEnded?.Invoke(this, EventArgs.Empty);
				}
			}
			else
			{
				// No lightshows in the queue, wait for a short period before checking again
				await Task.Delay(TimeSpan.FromSeconds(1), stoppingToken);
			}
		}

	}
}

public record LightshowSettings(string Name, TimeSpan Duration, string MusicFilePath, string LightPatternFilePath);
