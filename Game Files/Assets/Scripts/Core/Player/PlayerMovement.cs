using System.Collections;
using System.Collections.Generic;
using Unity.Netcode;
using UnityEngine;
using System.IO;
using Unity.VisualScripting;
using System;

public class PlayerMovement : NetworkBehaviour
{
    [Header("References")]
    [SerializeField] private InputReader inputReader;
    [SerializeField] private Transform bodyTransform;
    [SerializeField] private Rigidbody2D rb;
    [SerializeField] private ParticleSystem dustTrail;

    [Header("Settings")]
    [SerializeField] private float movementSpeed = 4f;
    [SerializeField] private float turningRate = 30f;
    [SerializeField] private float emissionRate = 10f;
    private string path;
   

    private ParticleSystem.EmissionModule emissionModule;
    private Vector2 previousMovementInput;
    private Vector3 previousPos;

    private const float ParticleStopThreshhold = 0.005f;
    
    
    private void Awake()
    {
        emissionModule = dustTrail.emission;
        path = Path.Combine(Application.persistentDataPath, "angle.txt");
    }

    public override void OnNetworkSpawn()
    {
        if (!IsOwner) { return; }

        inputReader.MoveEvent += HandleMove;
    }

    public override void OnNetworkDespawn()
    {
        if (!IsOwner) { return; }

        inputReader.MoveEvent -= HandleMove;
    }

    private void Update()
    {
        if (!IsOwner) { return; }

        float zRotation = previousMovementInput.x * -turningRate * Time.deltaTime;
        
        bodyTransform.Rotate(0f, 0f, zRotation);



        
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

    private void FixedUpdate()
    {
        if ((transform.position - previousPos).sqrMagnitude > ParticleStopThreshhold)
        {
            emissionModule.rateOverTime = emissionRate;
        }
        else
        {
            emissionModule.rateOverTime = 0;
        }

        previousPos = transform.position;

        if (!IsOwner) { return; }

        rb.velocity = (Vector2)bodyTransform.up * previousMovementInput.y * movementSpeed;

        string content = bodyTransform.eulerAngles.z.ToString();

        WriteToFile(path, content);
    }

    private void HandleMove(Vector2 movementInput)
    {
        previousMovementInput = movementInput;
    }
}
