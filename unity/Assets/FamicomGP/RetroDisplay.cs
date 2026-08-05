using UnityEngine;
using UnityEngine.UI;

namespace FamicomGP
{
    /// <summary>Renders the game at 320x180 and blows it up with point filtering. The
    /// chunky pixels are the whole look, so this is not a post effect but the display
    /// itself.</summary>
    public static class RetroDisplay
    {
        public const int Width = 320;
        public const int Height = 180;

        public static RenderTexture Attach(Camera cam)
        {
            var rt = new RenderTexture(Width, Height, 24, RenderTextureFormat.Default)
            {
                name = "FamicomGP_Screen",
                filterMode = FilterMode.Point,
                antiAliasing = 1
            };
            rt.Create();
            cam.targetTexture = rt;

            var canvasGo = new GameObject("RetroCanvas");
            var canvas = canvasGo.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = -100;
            canvasGo.AddComponent<CanvasScaler>();

            var imageGo = new GameObject("Screen");
            imageGo.transform.SetParent(canvasGo.transform, false);

            var raw = imageGo.AddComponent<RawImage>();
            raw.texture = rt;
            raw.raycastTarget = false;

            // The fitter drives the size, so the rect must be centre-anchored rather than
            // stretched — stretching fights the fitter and crops the picture.
            var rect = raw.rectTransform;
            rect.anchorMin = new Vector2(0.5f, 0.5f);
            rect.anchorMax = new Vector2(0.5f, 0.5f);
            rect.pivot = new Vector2(0.5f, 0.5f);
            rect.anchoredPosition = Vector2.zero;
            rect.sizeDelta = new Vector2(Width, Height);

            var fitter = imageGo.AddComponent<AspectRatioFitter>();
            fitter.aspectMode = AspectRatioFitter.AspectMode.FitInParent;
            fitter.aspectRatio = Width / (float)Height;

            return rt;
        }
    }

    /// <summary>Chase camera pinned to the track rather than to the car, which keeps the
    /// road centred the way the arcade original did.</summary>
    public class ChaseCamera : MonoBehaviour
    {
        public TrackBuilder track;
        public Racer target;

        [Tooltip("How far behind the car the camera sits. Pole Position kept it close.")]
        public float trail = 8.5f;

        [Tooltip("Camera height. Low is what makes the road fill the screen.")]
        public float lift = 2.9f;

        [Tooltip("How far up the road the camera aims. Lower puts the horizon higher.")]
        public float aheadLook = 26f;

        [Tooltip("How much the camera slides sideways with the car. Near zero keeps the " +
                 "camera on the road and lets the car visibly move across the screen.")]
        public float lateralFollow = 0.18f;

        Vector3 _pos;
        Vector3 _aim;
        bool _seeded;

        void LateUpdate()
        {
            if (track == null || target == null) return;

            Vector3 basePos, fwd;
            track.Sample(Mathf.Max(0f, target.distance - trail), out basePos, out fwd);
            Vector3 right = TrackBuilder.RightOf(fwd);

            Vector3 wantPos = basePos + Vector3.up * lift
                            + right * (target.lateral * TrackBuilder.RoadHalfWidth * lateralFollow);

            Vector3 wantAim = track.PointAt(
                Mathf.Min(track.TotalLength, target.distance + aheadLook),
                target.lateral * lateralFollow) + Vector3.up * 1.1f;

            if (!_seeded) { _pos = wantPos; _aim = wantAim; _seeded = true; }

            float k = 1f - Mathf.Exp(-9f * Time.deltaTime);
            _pos = Vector3.Lerp(_pos, wantPos, k);
            _aim = Vector3.Lerp(_aim, wantAim, k);

            transform.position = _pos;
            transform.rotation = Quaternion.LookRotation((_aim - _pos).normalized, Vector3.up);
        }
    }
}
