using UnityEngine;

namespace FamicomGP
{
    /// <summary>
    /// Starts the game on Play even in an empty or unrelated scene, so the project runs
    /// without anything being placed by hand. If a GameBootstrap is already in the scene
    /// this stays out of the way.
    /// </summary>
    public static class AutoLaunch
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void Launch()
        {
#if UNITY_2023_1_OR_NEWER
            var existing = Object.FindFirstObjectByType<GameBootstrap>();
#else
            var existing = Object.FindObjectOfType<GameBootstrap>();
#endif
            if (existing != null) return;

            var go = new GameObject("FamicomGP Bootstrap");
            go.AddComponent<GameBootstrap>();
        }
    }
}
