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

	private CancellationTokenSource? _skipTokenSource;
	private System.Diagnostics.Process? _currentMusicProcess;
	private int _currentVolume = 70; // Default volume at 70%

	public LightshowSettings? CurrentLightshow { get; private set; } = null!;

	public void EnqueueLightshow(LightshowSettings lightshow)
	{
		LightshowQueue.Enqueue(lightshow);
		QueueChanged?.Invoke(this, EventArgs.Empty);
	}

	public void SkipCurrentShow()
	{
		if (CurrentLightshow != null && _skipTokenSource != null && !_skipTokenSource.IsCancellationRequested)
		{
			logger.LogInformation($"Skipping current lightshow: {CurrentLightshow.Name}");
			_skipTokenSource.Cancel();
		}
	}

	public void SetVolume(int volume)
	{
		_currentVolume = Math.Clamp(volume, 0, 100);
		logger.LogInformation($"Volume set to: {_currentVolume}%");
		
		// Use amixer to control system volume (affects all audio output including Bluetooth)
		try
		{
			var amixerProcess = new System.Diagnostics.Process
			{
				StartInfo = new System.Diagnostics.ProcessStartInfo
				{
					FileName = "amixer",
					Arguments = $"sset 'Master' {_currentVolume}%",
					UseShellExecute = false,
					CreateNoWindow = true,
					RedirectStandardOutput = true,
					RedirectStandardError = true
				}
			};
			
			amixerProcess.Start();
			amixerProcess.WaitForExit(1000); // Wait up to 1 second
			
			if (amixerProcess.ExitCode == 0)
			{
				logger.LogInformation($"Successfully set system volume to {_currentVolume}%");
			}
			else
			{
				var error = amixerProcess.StandardError.ReadToEnd();
				logger.LogWarning($"amixer returned non-zero exit code. Error: {error}");
			}
		}
		catch (Exception ex)
		{
			logger.LogError(ex, "Failed to set system volume using amixer");
		}
	}

	public static readonly LightshowSettings[] AvailableLightshows =
	[
		new("Santa Claus Is Comin To Town", new TimeSpan(0, 4, 28), "wwwroot/music/Bruce Springsteen - Santa Claus Is Comin To Town (Official Audio).mp3", "wwwroot/lights/bruce-springsteen-santa-claus.json"),
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

	// Scrolling idle display when no shows are queued
	private static readonly LightshowSettings IdleDisplay = 
		new("Merry Christmas", new TimeSpan(0, 0, 12), "", "lights/merry-christmas-scrolling.json");

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

				// Create a new skip token source for this show
				_skipTokenSource = CancellationTokenSource.CreateLinkedTokenSource(stoppingToken);

				try
				{
					// Start playing the music using mplayer
					var musicProcess = new System.Diagnostics.Process
					{
						StartInfo = new System.Diagnostics.ProcessStartInfo
						{
							FileName = "mplayer",
							Arguments = $"-volume {_currentVolume} -ao pulse -really-quiet -nolirc \"{lightshowSettings.MusicFilePath}\"",
							UseShellExecute = false,
							CreateNoWindow = true,
							RedirectStandardOutput = true,
							RedirectStandardError = true,
							RedirectStandardInput = true,
							Environment = 
							{
								["TERM"] = "dumb",
								["PULSE_SERVER"] = "unix:/run/user/1000/pulse/native"
							}
						}
					};
					
					musicProcess.Start();
					_currentMusicProcess = musicProcess;
					
					logger.LogInformation($"Started music playback for: {lightshowSettings.Name} at {_currentVolume}% volume (PID: {musicProcess.Id})");

					// Start the LED light show in parallel
					var ledTask = Task.Run(async () =>
					{
						await ledService.PlayLedPattern(lightshowSettings, _skipTokenSource.Token);
					}, _skipTokenSource.Token);

					// Wait for the music to finish (use duration as max wait time)
					var musicTask = Task.Run(async () =>
					{
						await musicProcess.WaitForExitAsync(_skipTokenSource.Token);
					}, _skipTokenSource.Token);

					// Wait for both tasks to complete or use the duration as a timeout
					await Task.WhenAny(
						Task.WhenAll(musicTask, ledTask),
						Task.Delay(lightshowSettings.Duration.Add(TimeSpan.FromSeconds(2)), _skipTokenSource.Token)
					);

					// Ensure the process is stopped
					if (!musicProcess.HasExited)
					{
						musicProcess.Kill();
					}

					logger.LogInformation($"Finished lightshow: {lightshowSettings.Name}");
				}
				catch (OperationCanceledException)
				{
					logger.LogInformation($"Lightshow skipped: {lightshowSettings.Name}");
					
					// Kill the music process if it's still running
					if (_currentMusicProcess != null && !_currentMusicProcess.HasExited)
					{
						try
						{
							_currentMusicProcess.Kill();
							logger.LogInformation($"Stopped music process for skipped show");
						}
						catch (Exception ex)
						{
							logger.LogWarning(ex, $"Error stopping music process: {ex.Message}");
						}
					}
				}
				catch (Exception ex)
				{
					logger.LogError(ex, $"Error playing lightshow: {lightshowSettings.Name}");
				}
				finally
				{
					_skipTokenSource?.Dispose();
					_skipTokenSource = null;
					_currentMusicProcess = null;
					CurrentLightshow = null;
					LightshowEnded?.Invoke(this, EventArgs.Empty);
				}
			}
			else
			{
				// No lightshows in the queue, play the idle display
				await PlayIdleDisplay(stoppingToken);
			}
		}

	}

	private async Task PlayIdleDisplay(CancellationToken stoppingToken)
	{
		logger.LogInformation("Queue empty, starting idle display: {Name}", IdleDisplay.Name);
		CurrentLightshow = IdleDisplay;
		QueueChanged?.Invoke(this, EventArgs.Empty);

		using var idleCts = CancellationTokenSource.CreateLinkedTokenSource(stoppingToken);

		try
		{
			// Start the LED pattern
			var ledTask = Task.Run(async () =>
			{
				await ledService.PlayLedPattern(IdleDisplay, idleCts.Token);
			}, idleCts.Token);

			// Check periodically if a new show has been queued
			while (!idleCts.Token.IsCancellationRequested)
			{
				// If something is in the queue, cancel the idle display
				if (!LightshowQueue.IsEmpty)
				{
					logger.LogInformation("New show queued, stopping idle display");
					idleCts.Cancel();
					break;
				}

				// Wait a short period before checking again
				await Task.Delay(TimeSpan.FromMilliseconds(500), idleCts.Token);
			}

			// Wait for LED task to complete
			try
			{
				await ledTask;
			}
			catch (OperationCanceledException)
			{
				// Expected when cancelled
			}
		}
		catch (OperationCanceledException)
		{
			// Expected when service is stopping
		}
		finally
		{
			CurrentLightshow = null;
			QueueChanged?.Invoke(this, EventArgs.Empty);
		}
	}
}

public record LightshowSettings(string Name, TimeSpan Duration, string MusicFilePath, string LightPatternFilePath);
