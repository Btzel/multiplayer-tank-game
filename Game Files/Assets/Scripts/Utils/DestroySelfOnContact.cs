using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DestroySelfOnContact : MonoBehaviour
{
    [SerializeField] private Projectile projectie;

    private void OnTriggerEnter2D(Collider2D col)
    {
        if (projectie.TeamIndex != -1)
        {
            if (col.attachedRigidbody != null)
            {
                if (col.attachedRigidbody.TryGetComponent<TankPlayer>(out TankPlayer player))
                {
                    if (player.TeamIndex.Value == projectie.TeamIndex)
                    {
                        return;
                    }
                }
            }
        }

        Destroy(gameObject);
    }
}
