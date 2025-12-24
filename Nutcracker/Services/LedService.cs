using System.Drawing;
using System.Runtime.InteropServices;
using System.Text.Json;
using static Nutcracker.Services.Ws2811Native;

namespace Nutcracker.Services;

public class LedService : IDisposable
{
	private readonly ILogger<LedService> _logger;
	private readonly IWebHostEnvironment _environment;
	private readonly bool _isRaspberryPi;
	private readonly int _ledCount;
	private readonly int _matrixWidth;
	private readonly int _matrixHeight;
	private ws2811_t _ws2811;
	private bool _initialized;
	private readonly object _lock = new();
	private byte _currentBrightness = 26; // Track current brightness (0-255), start at 10%

	// LED Strip Configuration - SPI Mode
	private const int GPIO_PIN = 10;        // SPI0 MOSI - GPIO 10 (Physical Pin 19)
	private const int DMA_CHANNEL = 10;     // DMA channel (10 is usually safe)
	private const uint TARGET_FREQ = 800000; // 800kHz for WS2812B
	private const byte DEFAULT_BRIGHTNESS = 26; // 10% brightness (0-255)

	public LedService(ILogger<LedService> logger, IWebHostEnvironment environment)
	{
		_logger = logger;
		_environment = environment;
		_matrixWidth = 32;
		_matrixHeight = 8;
		_ledCount = _matrixWidth * _matrixHeight;
		_currentBrightness = DEFAULT_BRIGHTNESS; // Initialize brightness
		
		// Enhanced platform detection with logging
		var isLinux = RuntimeInformation.IsOSPlatform(OSPlatform.Linux);
		var architecture = RuntimeInformation.ProcessArchitecture;
		_logger.LogInformation("Platform detection: OS={Os}, Architecture={Architecture}", 
			isLinux ? "Linux" : "Other", architecture);
		
		_isRaspberryPi = isLinux && (architecture == Architecture.Arm || architecture == Architecture.Arm64);
		_logger.LogInformation("Raspberry Pi detected: {IsRaspberryPi}", _isRaspberryPi);

		Initialize();
	}

	/// <summary>
	/// Enhanced test method to light up LEDs across the full 8x32 matrix to verify hardware is working
	/// </summary>
	public async Task TestLeds()
	{
		_logger.LogInformation("=== LED TEST START ===");
		_logger.LogInformation("Matrix configuration: {Width}x{Height} = {Count} LEDs", _matrixWidth, _matrixHeight, _ledCount);
		_logger.LogInformation("Raspberry Pi detected: {IsRaspberryPi}", _isRaspberryPi);
		_logger.LogInformation("LED service initialized: {Initialized}", _initialized);
		_logger.LogInformation("Using GPIO pin: {Pin}", GPIO_PIN);

		if (!_initialized)
		{
			_logger.LogWarning("LED service not initialized - running in mock mode");
			_logger.LogWarning("If on Raspberry Pi, check: sudo permissions, libws2811 library installed, GPIO access");
			// Continue with mock test for demonstration
		}

		try
		{
			// Test 1: Fill entire matrix with red
			_logger.LogInformation("Test 1: Filling entire matrix with red ({Count} LEDs)", _ledCount);
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.FromArgb(255, 0, 0));
			}
			UpdateDisplay();
			_logger.LogInformation("Red fill complete, waiting 2 seconds...");
			await Task.Delay(2000);

			// Test 2: Fill entire matrix with green
			_logger.LogInformation("Test 2: Filling entire matrix with green");
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.FromArgb(0, 255, 0));
			}
			UpdateDisplay();
			_logger.LogInformation("Green fill complete, waiting 2 seconds...");
			await Task.Delay(2000);

			// Test 3: Fill entire matrix with blue
			_logger.LogInformation("Test 3: Filling entire matrix with blue");
			for (int i = 0; i < _ledCount; i++)
			{
				SetLedColor(i, Color.FromArgb(0, 0, 255));
			}
			UpdateDisplay();
			_logger.LogInformation("Blue fill complete, waiting 2 seconds...");
			await Task.Delay(2000);

			// Test 4: Test individual rows (8 rows)
			_logger.LogInformation("Test 4: Testing individual rows ({RowCount} rows)", _matrixHeight);
			await ClearAllLeds();
			for (int row = 0; row < _matrixHeight; row++)
			{
				await ClearAllLeds();
				_logger.LogInformation("Lighting row {Row}", row);
				for (int col = 0; col < _matrixWidth; col++)
				{
					int pixelIndex = row * _matrixWidth + col;
					SetLedColor(pixelIndex, Color.FromArgb(255, 255, 255)); // White
				}
				UpdateDisplay();
				await Task.Delay(500);
			}

			// Test 5: Test individual columns (32 columns) - abbreviated for logs
			_logger.LogInformation("Test 5: Testing individual columns ({ColCount} columns)", _matrixWidth);
			await ClearAllLeds();
			for (int col = 0; col < _matrixWidth; col++)
			{
				await ClearAllLeds();
				if (col % 8 == 0) // Log every 8th column
					_logger.LogDebug("Lighting column {Col}", col);
				
				for (int row = 0; row < _matrixHeight; row++)
				{
					int pixelIndex = row * _matrixWidth + col;
					SetLedColor(pixelIndex, Color.FromArgb(255, 255, 255)); // White
				}
				UpdateDisplay();
				await Task.Delay(100);
			}

			// Skip some tests for brevity, jump to final test
			_logger.LogInformation("Test 6: Scanning dot across first 50 LEDs");
			for (int pixelIndex = 0; pixelIndex < Math.Min(50, _ledCount); pixelIndex++)
			{
				await ClearAllLeds();
				SetLedColor(pixelIndex, Color.FromArgb(255, 255, 255));
				UpdateDisplay();
				await Task.Delay(50);
			}

			// Clear at end
			await ClearAllLeds();
			_logger.LogInformation("=== LED TEST COMPLETE ===");
		}
		catch (Exception ex)
		{
			_logger.LogError(ex, "Error during LED test");
		}
	}

	private void Initialize()
	{
		if (_isRaspberryPi)
		{
			try
			{
				_logger.LogInformation("Initializing LED strip on GPIO {Pin} SPI mode ({Count} LEDs) via native rpi_ws281x library", 
					GPIO_PIN, _ledCount);

				// Initialize the ws2811_t structure
				_ws2811 = new ws2811_t
				{
					freq = TARGET_FREQ,
					dmanum = DMA_CHANNEL,
					channel = new ws2811_channel_t[RPI_PWM_CHANNELS]
				};

				// Configure channel 0 (the one we're using)
				_ws2811.channel[0] = new ws2811_channel_t
				{
					gpionum = GPIO_PIN,
					count = _ledCount,
					invert = 0,
					brightness = _currentBrightness,
					strip_type = (int)WS2811_STRIP_GRB, // Most WS2812B use GRB order
					leds = Marshal.AllocHGlobal(_ledCount * 4) // Allocate LED buffer (4 bytes per LED)
				};

				// Clear the LED buffer
				for (int i = 0; i < _ledCount * 4; i++)
				{
					Marshal.WriteByte(_ws2811.channel[0].leds, i, 0);
				}

				// Configure channel 1 (unused)
				_ws2811.channel[1] = new ws2811_channel_t
				{
					gpionum = 0,
					count = 0,
					invert = 0,
					brightness = 0
				};

				// Initialize the library
				var result = ws2811_init(ref _ws2811);
				if (result != ws2811_return_t.WS2811_SUCCESS)
				{
					var errorMsg = Ws2811Native.GetErrorString(result);
					throw new Exception($"ws2811_init failed: {errorMsg}");
				}

				_initialized = true;
				_logger.LogInformation("LED strip initialized successfully on GPIO {Pin} (SPI mode)", GPIO_PIN);

				// Clear LEDs on startup
				ClearAllLeds().Wait();
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, "Failed to initialize LED strip. Running in mock mode.");
				_logger.LogWarning("Make sure to install the library: sudo apt-get install libws2811-dev");
				_logger.LogWarning("And run with sudo or proper permissions for GPIO access");
				_initialized = false;
				
				// Free allocated memory if initialization failed
				if (_ws2811.channel != null && _ws2811.channel[0].leds != IntPtr.Zero)
				{
					Marshal.FreeHGlobal(_ws2811.channel[0].leds);
					_ws2811.channel[0].leds = IntPtr.Zero;
				}
			}
		}
		else
		{
			_logger.LogWarning("Not running on Raspberry Pi. LED control will use mock mode.");
			_initialized = false;
		}
	}

	/// <summary>
	/// Get the current brightness level (0-100%)
	/// </summary>
	public int GetBrightness()
	{
		// Convert from byte value (0-255) to percentage (0-100)
		return (_currentBrightness * 100) / 255;
	}

	/// <summary>
	/// Set the brightness of the LED strip (0-100%)
	/// </summary>
	public void SetBrightness(int brightnessPercent)
	{
		// Convert from percentage (0-100) to byte value (0-255)
		var brightness = (byte)Math.Clamp((brightnessPercent * 255) / 100, 0, 255);
		_currentBrightness = brightness;
		
		_logger.LogInformation($"LED brightness set to: {brightnessPercent}% (raw: {brightness}/255)");
		
		if (_initialized && _ws2811.channel != null)
		{
			try
			{
				lock (_lock)
				{
					_ws2811.channel[0].brightness = _currentBrightness;
					// Render the update immediately to apply brightness change
					ws2811_render(ref _ws2811);
				}
				_logger.LogInformation("Brightness updated successfully");
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, "Failed to update LED brightness");
			}
		}
		else
		{
			_logger.LogWarning("LED service not initialized - brightness change will be applied when initialized");
		}
	}

	public async Task PlayLedPattern(LightshowSettings lightshowSettings, CancellationToken stoppingToken)
	{
		try
		{
			_logger.LogInformation("Starting LED pattern for: {Name}", lightshowSettings.Name);
			
			// Clear the display first to ensure clean slate
			await ClearAllLeds();
			
			// Load pattern from disk
			var pattern = await LoadPatternAsync(lightshowSettings.LightPatternFilePath);
			if (pattern == null)
			{
				_logger.LogWarning("No pattern loaded for {Name}, using fallback animation", lightshowSettings.Name);
				await PlayFallbackPattern(lightshowSettings.Duration, stoppingToken);
				return;
			}

			// If there's no music file (idle display), loop the pattern
			bool shouldLoop = string.IsNullOrEmpty(lightshowSettings.MusicFilePath);
			
			if (shouldLoop)
			{
				_logger.LogInformation("Looping pattern '{Name}' for idle display", pattern.Name);
				await PlayPatternLoopAsync(pattern, stoppingToken);
			}
			else
			{
				// Play the pattern once for music-synchronized shows
				await PlayPatternAsync(pattern, stoppingToken);
			}
			
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
			
			// Update the display to show the changes
			UpdateDisplay();
		}

		// Clear LEDs at the end
		await ClearAllLeds();
	}

	private async Task PlayPatternLoopAsync(LedPattern pattern, CancellationToken stoppingToken)
	{
		// Loop the pattern indefinitely until cancelled
		while (!stoppingToken.IsCancellationRequested)
		{
			var startTime = DateTime.UtcNow;
			var lastTimestamp = 0;

			// Group frames by timestamp to batch updates
			var framesByTimestamp = pattern.Frames
				.GroupBy(f => f.TimestampMs)
				.OrderBy(g => g.Key)
				.ToList();

			foreach (var frameGroup in framesByTimestamp)
			{
				if (stoppingToken.IsCancellationRequested)
					break;

				var timestamp = frameGroup.Key;
				
				// Wait until it's time to display this frame group
				var targetTime = startTime.AddMilliseconds(timestamp);
				var delay = targetTime - DateTime.UtcNow;
				
				if (delay > TimeSpan.Zero)
				{
					await Task.Delay(delay, stoppingToken);
				}

				// Apply all frames at this timestamp
				foreach (var frame in frameGroup)
				{
					ApplyFrame(frame);
				}
				
				// Update display once per timestamp
				UpdateDisplay();
				lastTimestamp = timestamp;
			}

			// No clear between loops - keep the last frame displayed
			// Add a small delay before restarting the loop
			if (!stoppingToken.IsCancellationRequested)
			{
				await Task.Delay(100, stoppingToken);
			}
		}

		// Clear LEDs when exiting
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

		// Note: UpdateDisplay is called only once per frame, not per effect
		// This allows multiple effects to be batched before rendering
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

		lock (_lock)
		{
			// Set the LED color in the buffer
			if (index >= 0 && index < _ledCount && _ws2811.channel[0].leds != IntPtr.Zero)
			{
				Ws2811Native.SetLedColor(_ws2811.channel[0].leds, index, color.R, color.G, color.B);
			}
		}
	}

	private void UpdateDisplay()
	{
		if (!_initialized)
			return;

		lock (_lock)
		{
			try
			{
				// Render the LED buffer to the strip
				var result = ws2811_render(ref _ws2811);
				if (result != ws2811_return_t.WS2811_SUCCESS)
				{
					_logger.LogError("Failed to render LEDs: {Error}", Ws2811Native.GetErrorString(result));
				}
			}
			catch (Exception ex)
			{
				_logger.LogError(ex, "Error updating LED display");
			}
		}
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

	/// <summary>
	/// Matrix-specific helper methods
	/// </summary>
	
	/// <summary>
	/// Convert row/column coordinates to linear LED index
	/// Assumes linear layout: row 0 = LEDs 0-31, row 1 = LEDs 32-63, etc.
	/// </summary>
	private int GetLedIndex(int row, int col)
	{
		if (row < 0 || row >= _matrixHeight || col < 0 || col >= _matrixWidth)
			return -1;
		
		return row * _matrixWidth + col;
	}

	/// <summary>
	/// Set LED color using row/column coordinates
	/// </summary>
	public void SetMatrixLed(int row, int col, Color color)
	{
		int index = GetLedIndex(row, col);
		if (index >= 0)
		{
			SetLedColor(index, color);
		}
	}

	/// <summary>
	/// Fill an entire row with a color
	/// </summary>
	public void FillRow(int row, Color color)
	{
		for (int col = 0; col < _matrixWidth; col++)
		{
			SetMatrixLed(row, col, color);
		}
	}

	/// <summary>
	/// Fill an entire column with a color
	/// </summary>
	public void FillColumn(int col, Color color)
	{
		for (int row = 0; row < _matrixHeight; row++)
		{
			SetMatrixLed(row, col, color);
		}
	}

	/// <summary>
	/// Create a moving wave effect across the matrix
	/// </summary>
	public async Task PlayMovingWave(TimeSpan duration, CancellationToken cancellationToken = default)
	{
		var startTime = DateTime.UtcNow;
		const int waveWidth = 5;

		while (DateTime.UtcNow - startTime < duration && !cancellationToken.IsCancellationRequested)
		{
			var elapsedMs = (DateTime.UtcNow - startTime).TotalMilliseconds;
			var wavePos = (int)(elapsedMs / 100) % (_matrixWidth + waveWidth); // Move across and off screen

			await ClearAllLeds();

			for (int row = 0; row < _matrixHeight; row++)
			{
				for (int col = 0; col < _matrixWidth; col++)
				{
					var distanceFromWave = Math.Abs(col - wavePos);
					if (distanceFromWave < waveWidth)
					{
						var brightness = Math.Max(0, 255 - (distanceFromWave * 51)); // Fade effect
						SetMatrixLed(row, col, Color.FromArgb(0, (int)brightness, (int)brightness));
					}
				}
			}

			UpdateDisplay();
			await Task.Delay(100, cancellationToken);
		}

		await ClearAllLeds();
	}

	/// <summary>
	/// Create a pulsing effect across the entire matrix
	/// </summary>
	public async Task PlayPulsingEffect(int pulses, CancellationToken cancellationToken = default)
	{
		for (int pulse = 0; pulse < pulses && !cancellationToken.IsCancellationRequested; pulse++)
		{
			// Fade in
			for (int brightness = 0; brightness <= 255; brightness += 5)
			{
				if (cancellationToken.IsCancellationRequested) break;
				
				for (int i = 0; i < _ledCount; i++)
				{
					SetLedColor(i, Color.FromArgb(brightness, 0, brightness)); // Purple
				}
				UpdateDisplay();
				await Task.Delay(20, cancellationToken);
			}

			// Fade out
			for (int brightness = 255; brightness >= 0; brightness -= 5)
			{
				if (cancellationToken.IsCancellationRequested) break;
				
				for (int i = 0; i < _ledCount; i++)
				{
					SetLedColor(i, Color.FromArgb(brightness, 0, brightness)); // Purple
				}
				UpdateDisplay();
				await Task.Delay(20, cancellationToken);
			}
		}

		await ClearAllLeds();
	}

	private async Task PlayFallbackPattern(TimeSpan duration, CancellationToken stoppingToken)
	{
		_logger.LogInformation("Playing comprehensive fallback animation for {Duration}ms", duration.TotalMilliseconds);
		
		var startTime = DateTime.UtcNow;
		var quarterDuration = TimeSpan.FromMilliseconds(duration.TotalMilliseconds / 4);

		try
		{
			// Pattern 1: Moving wave (25% of duration)
			_logger.LogDebug("Fallback pattern: Moving wave");
			await PlayMovingWave(quarterDuration, stoppingToken);
			
			if (stoppingToken.IsCancellationRequested) return;

			// Pattern 2: Pulsing effect (25% of duration)
			_logger.LogDebug("Fallback pattern: Pulsing effect");
			var pulsesNeeded = Math.Max(1, (int)(quarterDuration.TotalSeconds / 2)); // One pulse per 2 seconds
			await PlayPulsingEffect(pulsesNeeded, stoppingToken);
			
			if (stoppingToken.IsCancellationRequested) return;

			// Pattern 3: Row scan (25% of duration)
			_logger.LogDebug("Fallback pattern: Row scan");
			var rowScanStart = DateTime.UtcNow;
			while (DateTime.UtcNow - rowScanStart < quarterDuration && !stoppingToken.IsCancellationRequested)
			{
				for (int row = 0; row < _matrixHeight && !stoppingToken.IsCancellationRequested; row++)
				{
					await ClearAllLeds();
					FillRow(row, Color.FromArgb(0, 255, 0)); // Green
					UpdateDisplay();
					await Task.Delay(200, stoppingToken);
				}
			}

			if (stoppingToken.IsCancellationRequested) return;

			// Pattern 4: Column scan (25% of duration)
			_logger.LogDebug("Fallback pattern: Column scan");
			var colScanStart = DateTime.UtcNow;
			while (DateTime.UtcNow - colScanStart < quarterDuration && !stoppingToken.IsCancellationRequested)
			{
				for (int col = 0; col < _matrixWidth && !stoppingToken.IsCancellationRequested; col++)
				{
					await ClearAllLeds();
					FillColumn(col, Color.FromArgb(255, 0, 0)); // Red
					UpdateDisplay();
					await Task.Delay(50, stoppingToken);
				}
			}
		}
		catch (OperationCanceledException)
		{
			_logger.LogDebug("Fallback pattern cancelled");
		}
		finally
		{
			await ClearAllLeds();
		}
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
		if (_initialized)
		{
			_logger.LogInformation("Disposing LED service and clearing display");
			
			lock (_lock)
			{
				try
				{
					// Clear all LEDs before disposing
					for (int i = 0; i < _ledCount; i++)
					{
						if (_ws2811.channel[0].leds != IntPtr.Zero)
						{
							Ws2811Native.SetLedColor(_ws2811.channel[0].leds, i, 0, 0, 0);
						}
					}
					
					// Final render to show cleared state
					ws2811_render(ref _ws2811);
				}
				catch (Exception ex)
				{
					_logger.LogWarning(ex, "Error clearing LEDs during disposal");
				}

				try
				{
					// Cleanup native library
					ws2811_fini(ref _ws2811);
					
					// Free allocated LED buffer
					if (_ws2811.channel[0].leds != IntPtr.Zero)
					{
						Marshal.FreeHGlobal(_ws2811.channel[0].leds);
						_ws2811.channel[0].leds = IntPtr.Zero;
					}
				}
				catch (Exception ex)
				{
					_logger.LogWarning(ex, "Error during native library cleanup");
				}
				
				_initialized = false;
			}
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