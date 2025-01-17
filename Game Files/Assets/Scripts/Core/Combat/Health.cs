using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using Unity.Netcode;
using UnityEngine;

public class Health : NetworkBehaviour
{
    [field: SerializeField] public int MaxHealth { get; private set; } = 100;

    public NetworkVariable<int> CurrentHealth = new NetworkVariable<int>();
    private string path;
    private bool isDead;

    public Action<Health> OnDie;


    private void Start()
    {
        path = System.IO.Path.Combine(Application.persistentDataPath, "health.txt");
        Debug.Log($"Persistent Data Path: {Application.persistentDataPath}");
    }

    void WriteHealth(NetworkVariable<int> currentHealth, string path)
    {
        try
        {
            string health = currentHealth.Value.ToString();
            using (FileStream fs = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None))
            using (StreamWriter writer = new StreamWriter(fs))
            {
                writer.Write(health);
                writer.Flush();
            }
            Debug.Log($"Successfully wrote health to {path}");
        }
        catch (IOException ioEx)
        {
            Debug.LogError($"IOException: {ioEx.Message}");
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to write health data: {ex}");
        }
    }

    private void FixedUpdate()
    {
        if (!IsOwner) { return; }
        WriteHealth(CurrentHealth, path);
    }
    public override void OnNetworkSpawn()
    {
        if (!IsServer) { return; }

        CurrentHealth.Value = MaxHealth;
    }

    public void TakeDamage(int damageValue)
    {
        ModifyHealth(-damageValue);
    }

    public void RestoreHealth(int healValue)
    {
        ModifyHealth(healValue);
    }

    private void ModifyHealth(int value)
    {
        if (isDead) { return; }

        int newHealth = CurrentHealth.Value + value;
        CurrentHealth.Value = Mathf.Clamp(newHealth, 0, MaxHealth);

        if(CurrentHealth.Value == 0)
        {
            OnDie?.Invoke(this);
            isDead = true;
        }
    }
}
