using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Projectile : MonoBehaviour
{
    public int TeamIndex { get; private set; }

    public void Initialise(int teamIndex)
    {
        TeamIndex = teamIndex;
    }
}
