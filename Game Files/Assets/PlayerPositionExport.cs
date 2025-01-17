using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Unity.Netcode;
using System;

public class PlayerPositionExport : NetworkBehaviour
{
    private string path;
    private string path2;

    public Transform bodyTransform;
    public Transform pixelTransform;

    private void Start()
    {
        path = Path.Combine(Application.persistentDataPath, "player.txt");
        path2 = Path.Combine(Application.persistentDataPath, "reference.txt");
        Debug.Log($"Position data will be saved to: {path}");
        Debug.Log($"Pixel position data will be saved to: {path2}");
    }

    private void FixedUpdate()
    {
        if (!IsOwner) { return; }

        string pos = new Vector2(bodyTransform.transform.position.x, bodyTransform.transform.position.y).ToString();
        string pos2 = new Vector2(pixelTransform.transform.position.x, pixelTransform.transform.position.y).ToString();

        WriteToFile(path, pos);
        WriteToFile(path2, pos2);
    }

    private void WriteToFile(string filePath, string content)
    {
        try
        {
            using (FileStream fs = new FileStream(filePath, FileMode.Create, FileAccess.Write, FileShare.None))
            using (StreamWriter writer = new StreamWriter(fs))
            {
                writer.Write(content);
                writer.Flush();
            }
            Debug.Log($"Successfully wrote to {filePath}");
        }
        catch (IOException ioEx)
        {
            Debug.LogError($"IOException: {ioEx.Message} at {filePath}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to write data: {ex.Message} at {filePath}");
        }
    }
}
