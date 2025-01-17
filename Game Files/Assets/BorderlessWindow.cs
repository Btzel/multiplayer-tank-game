using System;
using System.Runtime.InteropServices;
using UnityEngine;

public class BorderlessWindow : MonoBehaviour
{
    [DllImport("user32.dll", EntryPoint = "SetWindowLong")]
    private static extern IntPtr SetWindowLongPtr(IntPtr hWnd, int nIndex, int dwNewLong);

    [DllImport("user32.dll", EntryPoint = "GetWindowLong")]
    private static extern int GetWindowLongPtr(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetWindowPos")]
    private static extern bool SetWindowPos(IntPtr hWnd, int hWndInsertAfter, int x, int y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll", EntryPoint = "FindWindow")]
    private static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    private const int GWL_STYLE = -16;
    private const int WS_BORDER = 1;
    private const int WS_DLGFRAME = 0x00400000;
    private const int WS_CAPTION = 0x00C00000;
    private const uint SWP_NOZORDER = 0x0004;
    private const uint SWP_NOACTIVATE = 0x0010;

    private void Start()
    {
        Screen.SetResolution(800, 600, false);

        var windowPtr = FindWindow(null, Application.productName);
        if (windowPtr != IntPtr.Zero)
        {
            int style = GetWindowLongPtr(windowPtr, GWL_STYLE);
            SetWindowLongPtr(windowPtr, GWL_STYLE, style & ~WS_BORDER & ~WS_DLGFRAME & ~WS_CAPTION);

            SetWindowPos(windowPtr, 0, 0, 0, 800, 600, SWP_NOZORDER | SWP_NOACTIVATE);
        }
    }
}
