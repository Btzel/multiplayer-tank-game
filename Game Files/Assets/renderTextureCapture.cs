using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class renderTextureCapture : MonoBehaviour
{
    public Camera captureCamera; // Assign your camera in the Inspector
    public string savePath = "C:\\Users\\ASUS\\Desktop\\MTG_Computer_Vision_Bot\\Map"; // Example: "/Users/YourUsername/Desktop/"

    private void Start()
    {
        if (!Directory.Exists(savePath))
        {
            Debug.LogError("Save path does not exist!");
        }
    }

    public void CaptureAndSave()
    {
        // Create a render texture with the same dimensions as the screen
        RenderTexture renderTexture = new RenderTexture(Screen.width, Screen.height, 24);

        // Set the camera's target texture to the render texture
        captureCamera.targetTexture = renderTexture;

        // Render the camera's view to the texture
        captureCamera.Render();

        // Create a new texture 2D to read the render texture's data
        Texture2D screenshot = new Texture2D(renderTexture.width, renderTexture.height, TextureFormat.RGB24, false);

        // Read pixels from the render texture and apply them to the texture 2D
        RenderTexture.active = renderTexture;
        screenshot.ReadPixels(new Rect(0, 0, renderTexture.width, renderTexture.height), 0, 0);
        screenshot.Apply();

        // Reset the camera's target texture to null
        captureCamera.targetTexture = null;
        RenderTexture.active = null;

        // Convert the texture 2D to bytes
        byte[] bytes = screenshot.EncodeToPNG();

        // Generate a file path with a unique name (e.g., based on timestamp)
        string fileName = "Map" + ".png";
        string filePath = savePath + fileName;

        // Write the bytes to the file
        File.WriteAllBytes(filePath, bytes);

        Debug.Log("Screenshot saved to: " + filePath);
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.O))
        {
            CaptureAndSave();
        }
    }
}
