using UnityEngine;

namespace FamicomGP
{
    /// <summary>
    /// The whole game assembles itself from this one component: track, backdrop, cars,
    /// camera and HUD. Drop it on an empty object in an empty scene and press Play —
    /// there is nothing to wire up by hand.
    /// </summary>
    [AddComponentMenu("Famicom GP/Game Bootstrap")]
    public class GameBootstrap : MonoBehaviour
    {
        [Tooltip("Leave on to have the attract-mode driver run laps until Space is pressed.")]
        public bool startInDemoMode = true;

        [Tooltip("Target frame rate. 60 keeps the arcade feel; the fixed low-res buffer " +
                 "means this is cheap even on a laptop.")]
        public int targetFrameRate = 60;

        void Awake()
        {
            Application.targetFrameRate = targetFrameRate;
            QualitySettings.vSyncCount = 0;

            ClearScene();

            var root = new GameObject("FamicomGP").transform;

            // ---------------------------------------------------------------- track
            var track = root.gameObject.AddComponent<TrackBuilder>();
            track.Build();

            var trackRoot = new GameObject("Track").transform;
            trackRoot.SetParent(root, false);
            track.BuildMeshes(trackRoot);

            // --------------------------------------------------------------- camera
            var camGo = new GameObject("RetroCamera");
            camGo.transform.SetParent(root, false);
            var cam = camGo.AddComponent<Camera>();
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = Palette.Sky;
            cam.fieldOfView = 62f;
            cam.nearClipPlane = 0.3f;
            cam.farClipPlane = 2400f;
            camGo.AddComponent<AudioListener>();

            RetroDisplay.Attach(cam);
            Backdrop.Create(camGo.transform);

            // ----------------------------------------------------------------- cars
            var player = MakeCar("PlayerCar", CarArt.Hero, root, track, camGo.transform);
            player.mode = Racer.Mode.Player;
            player.maxSpeed = 122f;
            player.accel = 36f;
            player.autoDrive = startInDemoMode;

            var rivals = new[]
            {
                MakeRival("Rival_Orange", CarArt.Orange, root, track, camGo.transform, 0.760f, -0.42f, 0.9f),
                MakeRival("Rival_Green",  CarArt.Green,  root, track, camGo.transform, 0.792f,  0.34f, 1.4f),
                MakeRival("Rival_Yellow", CarArt.Yellow, root, track, camGo.transform, 0.826f, -0.10f, 0.6f)
            };

            var chase = camGo.AddComponent<ChaseCamera>();
            chase.track = track;
            chase.target = player;

            // ---------------------------------------------------------------- race
            var manager = root.gameObject.AddComponent<RaceManager>();
            manager.track = track;
            manager.player = player;
            manager.rivals = rivals;
        }

        /// <summary>Switches off cameras and listeners the scene already had — the stock
        /// Main Camera otherwise fights ours for the screen and the audio listener.</summary>
        static void ClearScene()
        {
#if UNITY_2023_1_OR_NEWER
            var cameras = Object.FindObjectsByType<Camera>(FindObjectsSortMode.None);
            var listeners = Object.FindObjectsByType<AudioListener>(FindObjectsSortMode.None);
#else
            var cameras = Object.FindObjectsOfType<Camera>();
            var listeners = Object.FindObjectsOfType<AudioListener>();
#endif
            foreach (var c in cameras) c.gameObject.SetActive(false);
            foreach (var l in listeners) l.enabled = false;
        }

        static Racer MakeCar(string name, CarArt.Livery livery, Transform parent,
                             TrackBuilder track, Transform cam)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            CarArt.Spawn("Sprite", livery, go.transform);

            var racer = go.AddComponent<Racer>();
            racer.track = track;
            racer.lookAt = cam;
            return racer;
        }

        static Racer MakeRival(string name, CarArt.Livery livery, Transform parent,
                               TrackBuilder track, Transform cam,
                               float speedFraction, float lane, float wobble)
        {
            var racer = MakeCar(name, livery, parent, track, cam);
            racer.mode = Racer.Mode.Rival;
            racer.maxSpeed = 122f * speedFraction;
            racer.targetLane = lane;
            racer.wobble = wobble;
            return racer;
        }
    }
}
