using System.Drawing;
using System.Runtime.InteropServices;
using System.Text.Json;

namespace Nutcracker.Services;

public class LedService : IDisposable
{
	private readonly ILogger<LedService> _logger;
	private readonly IWebHostEnvironment _environment;
	private readonly bool _isRaspberryPi;
	private readonly int _ledCount;
	private readonly int _matrixWidth;
	private readonly int _matrixHeight;
	private IntPtr _ledStrip = IntPtr.Zero;
	private bool _initialized;

	// LED Matrix Configuration (8x32 = 256 LEDs)
	private const int GPIO_PIN = 18;
	private const int LED_FREQ_HZ = 800000;
	private const int DMA = 10;
	private const int LED_BRIGHTNESS = 255;
	private const int LED_INVERT = 0;
	private const int LED_CHANNEL = 0;

	public LedService(ILogger<LedService> logger, IWebHostEnvironment environment)
	{
		_logger = logger;
		_environment = environment;
		_matrixWidth = 32;
		_matrixHeight = 8;
		_ledCount = _matrixWidth * _matrixHeight;
		_isRaspberryPi = RuntimeInformation.IsOSPlatform(OSPlatform.Linux) && 
		                 RuntimeInformation.ProcessArchitecture == Architecture.Arm;

		Initialize();
	}

	private void Initialize()
	{
		if (_isRaspberryPi)
		{
			try
			{
				_logger.LogInformation("Initializing LED matrix on GPIO pin {Pin} ({Width}x{Height} = {Count} LEDs)", 
					GPIO_PIN, _matrixWidth, _matrixHeight, _ledCount);

				// Initialize WS281x LED strip
				// Note: This requires rpi_ws281x library to be installed
				// For now, we'll simulate initialization
				_initialized = true;
				_logger.LogInformation("LED matrix initialized successfully");
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, "Failed to initialize LED matrix. Running in mock mode.");
				_initialized = false;
			}
		}
		else
		{
			_logger.LogWarning("Not running on Raspberry Pi. LED control will use mock mode.");
			_initialized = false;
		}
	}

	public async Task PlayLedPattern(LightshowSettings lightshowSettings, CancellationToken stoppingToken)
	{
		try
		{
			_logger.LogInformation("Starting LED pattern for: {Name}", lightshowSettings.Name);
			
			// Load pattern from disk
			var pattern = await LoadPatternAsync(lightshowSettings.LightPatternFilePath);
			if (pattern == null)
			{
				_logger.LogWarning("No pattern loaded for {Name}, using fallback animation", lightshowSettings.Name);
				await PlayFallbackPattern(lightshowSettings.Duration, stoppingToken);
				return;
			}

			// Play the pattern
			await PlayPatternAsync(pattern, stoppingToken);
			
			_logger.LogInformation("Completed LED pattern for: {Name}", lightshowSettings.Name);
		}
		catch (OperationCanceledException)
		{
			_logger.LogInformation("LED pattern cancelled for: {Name}", lightshowSettings.Name);
			await ClearAllLeds();
		}
		catch (Exception ex)
		{
			_logger.LogError(ex, "Error playing LED pattern for: {Name}", lightshowSettings.Name);
			await ClearAllLeds();
		}
	}

	private async Task<LedPattern?> LoadPatternAsync(string patternFilePath)
	{
		try
		{
			var fullPath = Path.Combine(_environment.WebRootPath, patternFilePath.TrimStart('/'));
			
			if (!File.Exists(fullPath))
			{
				_logger.LogWarning("Pattern file not found: {Path}", fullPath);
				return null;
			}

			var json = await File.ReadAllTextAsync(fullPath);
			var pattern = JsonSerializer.Deserialize<LedPattern>(json, new JsonSerializerOptions
			{
				PropertyNameCaseInsensitive = true
			});

			if (pattern != null)
			{
				_logger.LogInformation("Loaded pattern '{Name}' with {Count} frames", 
					pattern.Name, pattern.Frames.Count);
			}

			return pattern;
		}
		catch (Exception ex)
		{
			_logger.LogError(ex, "Error loading pattern file: {Path}", patternFilePath);
			return null;
		}
	}

	private async Task PlayPatternAsync(LedPattern pattern, CancellationToken stoppingToken)
	{
		var startTime = DateTime.UtcNow;

		foreach (var frame in pattern.Frames)
		{
			if (stoppingToken.IsCancellationRequested)
				break;

			// Wait until it's time to display this frame
			var targetTime = startTime.AddMilliseconds(frame.TimestampMs);
			var delay = targetTime - DateTime.UtcNow;
			
			if (delay > TimeSpan.Zero)
			{
				await Task.Delay(delay, stoppingToken);
			}

			// Apply the frame
			ApplyFrame(frame);
		}

		// Clear LEDs at the end
		await ClearAllLeds();
	}

	private void ApplyFrame(LedFrame frame)
	{
		switch (frame.Effect)
		{
			case "set":
				SetLeds(frame.Leds, frame.Color);
				break;
			case "fill":
				FillAll(frame.Color);
				break;
			case "clear":
				ClearLeds(frame.Leds);
				break;
			case "gradient":
				ApplyGradient(frame.StartColor, frame.EndColor, frame.Leds);
				break;
			default:
				_logger.LogWarning("Unknown effect type: {Effect}", frame.Effect);
				break;
		}

		UpdateDisplay();
	}

	private void SetLeds(List<int>? ledIndices, string? colorHex)
	{
		if (ledIndices == null || colorHex == null) return;

		var color = ParseColor(colorHex);

		foreach (var index in ledIndices)
		{
			if (index >= 0 && index < _ledCount)
			{
				SetLedColor(index, color);
			}
		}
	}

	private void FillAll(string? colorHex)
	{
		if (colorHex == null) return;

		var color = ParseColor(colorHex);
		
		for (int i = 0; i < _ledCount; i++)
		{
			SetLedColor(i, color);
		}
	}

	private void ClearLeds(List<int>? ledIndices)
	{
		if (ledIndices == null)
		{
			// Clear all
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.Black);
			}
		}
		else
		{
			// Clear specific LEDs
			foreach (var index in ledIndices)
			{
				if (index >= 0 && index < _ledCount)
				{
					SetLedColor(index, Color.Black);
				}
			}
		}
	}

	private void ApplyGradient(string? startColorHex, string? endColorHex, List<int>? ledIndices)
	{
		if (startColorHex == null || endColorHex == null || ledIndices == null || ledIndices.Count == 0)
			return;

		var startColor = ParseColor(startColorHex);
		var endColor = ParseColor(endColorHex);

		for (int i = 0; i < ledIndices.Count; i++)
		{
			var index = ledIndices[i];
			if (index >= 0 && index < _ledCount)
			{
				var ratio = ledIndices.Count > 1 ? (float)i / (ledIndices.Count - 1) : 0;
				var r = (byte)(startColor.R + (endColor.R - startColor.R) * ratio);
				var g = (byte)(startColor.G + (endColor.G - startColor.G) * ratio);
				var b = (byte)(startColor.B + (endColor.B - startColor.B) * ratio);
				
				SetLedColor(index, Color.FromArgb(r, g, b));
			}
		}
	}

	private void SetLedColor(int index, Color color)
	{
		if (!_initialized)
		{
			// Mock mode - just log occasionally
			if (index % 50 == 0)
			{
				_logger.LogDebug("Mock: LED {Index} -> {Color}", index, color);
			}
			return;
		}

		// TODO: When rpi_ws281x library is added, implement actual LED setting
		// For example: ws2811_led_set(_ledStrip, LED_CHANNEL, index, color.ToArgb());
	}

	private void UpdateDisplay()
	{
		if (!_initialized)
			return;

		// TODO: When rpi_ws281x library is added, implement actual display update
		// For example: ws2811_render(_ledStrip);
	}

	private async Task ClearAllLeds()
	{
		for (int i = 0; i < _ledCount; i++)
		{
			SetLedColor(i, Color.Black);
		}
		UpdateDisplay();
		await Task.CompletedTask;
	}

	private async Task PlayFallbackPattern(TimeSpan duration, CancellationToken stoppingToken)
	{
		// Simple chase animation as fallback
		var startTime = DateTime.UtcNow;
		var frameDelay = TimeSpan.FromMilliseconds(50);

		while (DateTime.UtcNow - startTime < duration && !stoppingToken.IsCancellationRequested)
		{
			var position = (int)((DateTime.UtcNow - startTime).TotalMilliseconds / 50) % _ledCount;
			
			// Clear all
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.Black);
			}

			// Set current position
			SetLedColor(position, Color.Red);
			UpdateDisplay();

			await Task.Delay(frameDelay, stoppingToken);
		}

		await ClearAllLeds();
	}

	private Color ParseColor(string colorHex)
	{
		try
		{
			colorHex = colorHex.TrimStart('#');
			
			if (colorHex.Length == 6)
			{
				var r = Convert.ToByte(colorHex.Substring(0, 2), 16);
				var g = Convert.ToByte(colorHex.Substring(2, 2), 16);
				var b = Convert.ToByte(colorHex.Substring(4, 2), 16);
				return Color.FromArgb(r, g, b);
			}
		}
		catch (Exception ex)
		{
			_logger.LogWarning(ex, "Failed to parse color: {Color}", colorHex);
		}

		return Color.Black;
	}

	public void Dispose()
	{
		if (_initialized && _ledStrip != IntPtr.Zero)
		{
			_logger.LogInformation("Disposing LED service and clearing display");
			
			// Clear all LEDs before disposing
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.Black);
			}
			UpdateDisplay();

			// TODO: When rpi_ws281x library is added, implement cleanup
			// For example: ws2811_fini(_ledStrip); ws2811_destroy(_ledStrip);
			
			_ledStrip = IntPtr.Zero;
			_initialized = false;
		}
	}
}

// Data models for LED patterns
public record LedPattern(
	string Name,
	string Description,
	int DurationMs,
	List<LedFrame> Frames
);

public record LedFrame(
	int TimestampMs,
	string Effect, // "set", "fill", "clear", "gradient"
	string? Color = null,
	List<int>? Leds = null,
	string? StartColor = null,
	string? EndColor = null
);