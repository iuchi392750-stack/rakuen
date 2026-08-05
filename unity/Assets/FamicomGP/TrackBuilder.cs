using System.Collections.Generic;
using UnityEngine;

namespace FamicomGP
{
    /// <summary>
    /// Procedural circuit: a centreline of evenly spaced points with banked curves and
    /// hills, plus the flat-shaded meshes (road, rumble strips, lane markings, verge,
    /// chequered finish line) drawn from it.
    /// </summary>
    public class TrackBuilder : MonoBehaviour
    {
        public const float SegmentLength = 4f;
        public const float RoadHalfWidth = 7f;
        public const float RumbleWidth = 1.6f;
        public const int Lanes = 3;

        public readonly List<Vector3> Center = new List<Vector3>();
        public float TotalLength { get; private set; }

        float _heading;
        float _height;
        Vector3 _cursor;

        // ------------------------------------------------------------------ build

        public void Build()
        {
            Center.Clear();
            _heading = 0f;
            _height = 0f;
            _cursor = Vector3.zero;
            Center.Add(_cursor);

            // start apron
            Section(70, 0f, 0f);
            Section(60, 0.9f, 0.06f);
            Section(30, 0f, 0f);
            Section(80, -1.5f, 0f);
            Section(50, 0f, 0.16f);
            Section(55, 2.4f, -0.08f);
            Section(45, 0f, 0f);
            Section(85, -0.9f, 0.22f);
            Section(60, 1.6f, -0.18f);
            Section(30, 0f, 0f);
            Section(60, -2.4f, 0f);
            Section(50, 0f, -0.16f);
            Section(80, 1.5f, 0.06f);
            Section(45, 0f, 0f);
            Section(55, -0.9f, -0.05f);
            Section(55, 0.9f, 0f);
            // finishing straight
            Section(110, 0f, 0f);

            TotalLength = (Center.Count - 1) * SegmentLength;
        }

        /// <summary>Appends `count` segments, easing the curve and slope in and out
        /// so sections meet without a visible kink.</summary>
        void Section(int count, float curveDegPerSeg, float risePerSeg)
        {
            for (int i = 0; i < count; i++)
            {
                float t = (float)i / count;
                float ease = Mathf.SmoothStep(0f, 1f, t < 0.5f ? t * 2f : (1f - t) * 2f);

                _heading += curveDegPerSeg * ease * Mathf.Deg2Rad;
                _height += risePerSeg * ease;

                Vector3 fwd = new Vector3(Mathf.Sin(_heading), 0f, Mathf.Cos(_heading));
                _cursor += fwd * SegmentLength;
                _cursor.y = _height;
                Center.Add(_cursor);
            }
        }

        // ----------------------------------------------------------------- sample

        public Vector3 Forward(int i)
        {
            i = Mathf.Clamp(i, 0, Center.Count - 2);
            return (Center[i + 1] - Center[i]).normalized;
        }

        public static Vector3 RightOf(Vector3 forward)
        {
            return Vector3.Cross(Vector3.up, forward).normalized;
        }

        /// <summary>Position and heading at a distance along the centreline.</summary>
        public void Sample(float distance, out Vector3 pos, out Vector3 forward)
        {
            float f = Mathf.Clamp(distance, 0f, TotalLength) / SegmentLength;
            int i = Mathf.Clamp(Mathf.FloorToInt(f), 0, Center.Count - 2);
            float t = Mathf.Clamp01(f - i);
            pos = Vector3.Lerp(Center[i], Center[i + 1], t);
            forward = Forward(i);
        }

        /// <summary>World point for a track distance plus a lateral offset in lanes
        /// (-1 = left edge, +1 = right edge).</summary>
        public Vector3 PointAt(float distance, float lateral)
        {
            Vector3 pos, fwd;
            Sample(distance, out pos, out fwd);
            return pos + RightOf(fwd) * (lateral * RoadHalfWidth);
        }

        // ------------------------------------------------------------------ mesh

        public void BuildMeshes(Transform parent)
        {
            AddMesh(parent, "Verge_L", Strip(-RoadHalfWidth - RumbleWidth - 90f, -RoadHalfWidth - RumbleWidth), Palette.Grass);
            AddMesh(parent, "Verge_R", Strip(RoadHalfWidth + RumbleWidth, RoadHalfWidth + RumbleWidth + 90f), Palette.Grass);

            AddMesh(parent, "Road", Strip(-RoadHalfWidth, RoadHalfWidth), Palette.Road);

            // rumble strips alternate in three-segment blocks
            AddMesh(parent, "Rumble_L_A", Strip(-RoadHalfWidth - RumbleWidth, -RoadHalfWidth, 2, 0), Palette.RumbleRed);
            AddMesh(parent, "Rumble_L_B", Strip(-RoadHalfWidth - RumbleWidth, -RoadHalfWidth, 2, 1), Palette.RumbleWhite);
            AddMesh(parent, "Rumble_R_A", Strip(RoadHalfWidth, RoadHalfWidth + RumbleWidth, 2, 0), Palette.RumbleRed);
            AddMesh(parent, "Rumble_R_B", Strip(RoadHalfWidth, RoadHalfWidth + RumbleWidth, 2, 1), Palette.RumbleWhite);

            // dashed lane markings
            float laneStep = (RoadHalfWidth * 2f) / Lanes;
            for (int lane = 1; lane < Lanes; lane++)
            {
                float x = -RoadHalfWidth + laneStep * lane;
                AddMesh(parent, "Lane" + lane, Strip(x - 0.18f, x + 0.18f, 3, 0), Palette.Line);
            }

            BuildFinishLine(parent);
        }

        /// <summary>A ribbon between two lateral offsets. When `modulo` is greater than
        /// one only every `modulo`-th three-segment block is emitted, which is what makes
        /// the rumble strips and lane dashes.</summary>
        Mesh Strip(float a, float b, int modulo = 1, int phase = 0)
        {
            var verts = new List<Vector3>();
            var tris = new List<int>();

            for (int i = 0; i < Center.Count - 1; i++)
            {
                if (modulo > 1 && (i / 3) % modulo != phase) continue;

                Vector3 r0 = RightOf(Forward(i));
                Vector3 r1 = RightOf(Forward(i + 1));
                int v = verts.Count;

                verts.Add(Center[i] + r0 * a);
                verts.Add(Center[i] + r0 * b);
                verts.Add(Center[i + 1] + r1 * b);
                verts.Add(Center[i + 1] + r1 * a);

                tris.Add(v); tris.Add(v + 2); tris.Add(v + 1);
                tris.Add(v); tris.Add(v + 3); tris.Add(v + 2);
            }

            var mesh = new Mesh { name = "Strip" };
            mesh.indexFormat = verts.Count > 65000
                ? UnityEngine.Rendering.IndexFormat.UInt32
                : UnityEngine.Rendering.IndexFormat.UInt16;
            mesh.SetVertices(verts);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        void BuildFinishLine(Transform parent)
        {
            int last = Center.Count - 2;
            int start = Mathf.Max(0, last - 3);
            float cell = (RoadHalfWidth * 2f) / 8f;

            for (int col = 0; col < 8; col++)
            {
                for (int row = 0; row < 2; row++)
                {
                    bool white = (col + row) % 2 == 0;
                    int i = Mathf.Clamp(start + row, 0, last);

                    Vector3 r0 = RightOf(Forward(i));
                    Vector3 r1 = RightOf(Forward(i + 1));
                    float a = -RoadHalfWidth + cell * col;
                    float b = a + cell;
                    Vector3 lift = Vector3.up * 0.02f;

                    var mesh = new Mesh { name = "Finish" };
                    mesh.SetVertices(new List<Vector3>
                    {
                        Center[i] + r0 * a + lift,
                        Center[i] + r0 * b + lift,
                        Center[i + 1] + r1 * b + lift,
                        Center[i + 1] + r1 * a + lift
                    });
                    mesh.SetTriangles(new List<int> { 0, 2, 1, 0, 3, 2 }, 0);
                    mesh.RecalculateNormals();
                    mesh.RecalculateBounds();

                    AddMesh(parent, "Finish", mesh, white ? Palette.Line : Palette.Ink);
                }
            }
        }

        static void AddMesh(Transform parent, string name, Mesh mesh, Color color)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            go.AddComponent<MeshRenderer>().sharedMaterial = Palette.Flat(color);
        }
    }
}
