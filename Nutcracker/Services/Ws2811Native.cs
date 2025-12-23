using System.Runtime.InteropServices;

namespace Nutcracker.Services;

/// <summary>
/// P/Invoke wrapper for the rpi_ws281x native library (libws2811.so)
/// This provides direct access to the WS2812B LED control library
/// Library: https://github.com/jgarff/rpi_ws281x
/// Install on Pi: sudo apt-get install libws2811-dev
/// </summary>
public static class Ws2811Native
{
    private const string LibraryName = "ws2811";

    // GPIO Pin types
    public const int RPI_PWM_CHANNELS = 2;
    
    // LED Strip types
    public const uint WS2811_STRIP_RGB = 0x00100800;
    public const uint WS2811_STRIP_RBG = 0x00100008;
    public const uint WS2811_STRIP_GRB = 0x00081000;
    public const uint WS2811_STRIP_GBR = 0x00080010;
    public const uint WS2811_STRIP_BRG = 0x00001008;
    public const uint WS2811_STRIP_BGR = 0x00000810;

    // LED channel structure
    [StructLayout(LayoutKind.Sequential)]
    public struct ws2811_channel_t
    {
        public int gpionum;           // GPIO Pin number
        public int invert;            // Invert output signal
        public int count;             // Number of LEDs
        public int strip_type;        // Strip color layout
        public IntPtr leds;           // LED buffer (uint32_t array)
        public byte brightness;       // Brightness value (0-255)
        public byte wshift;           // White shift value
        public byte rshift;           // Red shift value
        public byte gshift;           // Green shift value
        public byte bshift;           // Blue shift value
        public IntPtr gamma;          // Gamma correction table
    }

    // Main device structure
    [StructLayout(LayoutKind.Sequential)]
    public struct ws2811_t
    {
        public long render_wait_time; // Time to wait for render completion
        public IntPtr device;         // Private device pointer
        public IntPtr rpi_hw;         // Private RPI hardware info
        public uint freq;             // Output frequency (typically 800000 Hz)
        public int dmanum;            // DMA number to use
        
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = RPI_PWM_CHANNELS)]
        public ws2811_channel_t[] channel; // Channel array (2 channels)
    }

    // Return codes
    public enum ws2811_return_t
    {
        WS2811_SUCCESS = 0,
        WS2811_ERROR_GENERIC = -1,
        WS2811_ERROR_OUT_OF_MEMORY = -2,
        WS2811_ERROR_HW_NOT_SUPPORTED = -3,
        WS2811_ERROR_MEM_LOCK = -4,
        WS2811_ERROR_MMAP = -5,
        WS2811_ERROR_MAP_REGISTERS = -6,
        WS2811_ERROR_GPIO_INIT = -7,
        WS2811_ERROR_PWM_SETUP = -8,
        WS2811_ERROR_MAILBOX_DEVICE = -9,
        WS2811_ERROR_DMA = -10,
        WS2811_ERROR_ILLEGAL_GPIO = -11,
        WS2811_ERROR_PCM_SETUP = -12,
        WS2811_ERROR_SPI_SETUP = -13,
        WS2811_ERROR_SPI_TRANSFER = -14
    }

    // Native function imports
    [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
    public static extern ws2811_return_t ws2811_init(ref ws2811_t ws2811);

    [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
    public static extern void ws2811_fini(ref ws2811_t ws2811);

    [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
    public static extern ws2811_return_t ws2811_render(ref ws2811_t ws2811);

    [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
    public static extern ws2811_return_t ws2811_wait(ref ws2811_t ws2811);

    [DllImport(LibraryName, CallingConvention = CallingConvention.Cdecl)]
    public static extern IntPtr ws2811_get_return_t_str(ws2811_return_t state);

    // Helper to get error string
    public static string GetErrorString(ws2811_return_t returnCode)
    {
        var ptr = ws2811_get_return_t_str(returnCode);
        return Marshal.PtrToStringAnsi(ptr) ?? $"Unknown error: {returnCode}";
    }

    // Helper to set LED color in the buffer
    public static void SetLedColor(IntPtr ledBuffer, int index, byte r, byte g, byte b)
    {
        if (ledBuffer == IntPtr.Zero) return;
        
        // WS2811 uses 32-bit color: 0x00RRGGBB
        uint color = (uint)((r << 16) | (g << 8) | b);
        Marshal.WriteInt32(ledBuffer, index * 4, (int)color);
    }

    // Helper to get LED color from buffer
    public static (byte r, byte g, byte b) GetLedColor(IntPtr ledBuffer, int index)
    {
        if (ledBuffer == IntPtr.Zero) return (0, 0, 0);
        
        uint color = (uint)Marshal.ReadInt32(ledBuffer, index * 4);
        byte r = (byte)((color >> 16) & 0xFF);
        byte g = (byte)((color >> 8) & 0xFF);
        byte b = (byte)(color & 0xFF);
        return (r, g, b);
    }
}
