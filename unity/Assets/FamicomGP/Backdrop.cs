using System.Collections.Generic;
using UnityEngine;

namespace FamicomGP
{
    /// <summary>A cylinder of sky, mountains and grandstands wrapped around the world and
    /// parented to the camera, so it parallaxes as the car turns without ever being
    /// reached.</summary>
    public static class Backdrop
    {
        const int TexW = 512;
        const int TexH = 128;

        public static GameObject Create(Transform follow)
        {
            var go = new GameObject("Backdrop");
            var mf = go.AddComponent<MeshFilter>();
            var mr = go.AddComponent<MeshRenderer>();

            mf.sharedMesh = Cylinder(900f, 520f, 48);

            var shader = Shader.Find("Unlit/Texture");
            if (shader == null) shader = Palette.SpriteShader;
            var mat = new Material(shader);
            mat.mainTexture = Paint();
            mr.sharedMaterial = mat;

            var rider = go.AddComponent<BackdropRider>();
            rider.follow = follow;
            return go;
        }

        /// <summary>Inward-facing cylinder: the winding is reversed so it is visible from
        /// inside.</summary>
        static Mesh Cylinder(float radius, float height, int sides)
        {
            var verts = new List<Vector3>();
            var uvs = new List<Vector2>();
            var tris = new List<int>();

            for (int i = 0; i <= sides; i++)
            {
                float t = (float)i / sides;
                float a = t * Mathf.PI * 2f;
                float x = Mathf.Sin(a) * radius;
                float z = Mathf.Cos(a) * radius;

                verts.Add(new Vector3(x, -height * 0.22f, z));
                verts.Add(new Vector3(x, height * 0.78f, z));
                uvs.Add(new Vector2(t, 0f));
                uvs.Add(new Vector2(t, 1f));
            }

            for (int i = 0; i < sides; i++)
            {
                int v = i * 2;
                tris.Add(v); tris.Add(v + 1); tris.Add(v + 2);
                tris.Add(v + 1); tris.Add(v + 3); tris.Add(v + 2);
            }

            var mesh = new Mesh { name = "BackdropCylinder" };
            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        static Texture2D Paint()
        {
            var tex = new Texture2D(TexW, TexH, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Repeat
            };

            // rows are bottom-up: 0 = ground, TexH = top of sky
            for (int y = 0; y < TexH; y++)
            {
                Color band = y > 96 ? Palette.Sky
                           : y > 88 ? Palette.SkyBand
                           : Palette.Grass;
                for (int x = 0; x < TexW; x++) tex.SetPixel(x, y, band);
            }

            // mountain range
            for (int i = 0; i < 14; i++)
            {
                int peakX = i * 38 + 18;
                int peakH = 34 + (i * 11) % 20;
                for (int row = 0; row < peakH; row++)
                {
                    int halfW = Mathf.RoundToInt((row / (float)peakH) * peakH);
                    int y = 88 + peakH - row;
                    Color c = row < peakH * 0.3f ? Palette.Snow : Palette.Mountain;
                    for (int dx = -halfW; dx <= halfW; dx++)
                        tex.SetPixel(Wrap(peakX + dx), Mathf.Clamp(y, 0, TexH - 1), c);
                }
            }

            // grandstands with a speckled crowd
            var crowd = new[] { "fc5454", "fcd800", "fcfcfc", "54d8fc", "f87800", "c84c9c" };
            for (int s = 0; s < TexW; s += 128)
            {
                for (int x = 6; x < 118; x++)
                {
                    for (int y = 74; y < 90; y++)
                    {
                        Color c;
                        if (y >= 86) c = Palette.Stand;
                        else if (y >= 84) c = Palette.Hex("d8d8e8");
                        else c = Palette.Hex(crowd[(x * 7 + y * 31) % crowd.Length]);
                        tex.SetPixel(Wrap(s + x), y, c);
                    }
                }
            }

            // blocky clouds
            for (int i = 0; i < 8; i++)
            {
                int cx = i * 64 + 12;
                int cy = 108 + (i * 5) % 12;
                Block(tex, cx, cy, 26, 4);
                Block(tex, cx + 5, cy + 4, 16, 4);
                Block(tex, cx + 10, cy + 8, 8, 3);
            }

            tex.Apply();
            return tex;
        }

        static void Block(Texture2D tex, int x, int y, int w, int h)
        {
            for (int dx = 0; dx < w; dx++)
                for (int dy = 0; dy < h; dy++)
                    tex.SetPixel(Wrap(x + dx), Mathf.Clamp(y + dy, 0, TexH - 1), Palette.Snow);
        }

        static int Wrap(int x) { return ((x % TexW) + TexW) % TexW; }
    }

    /// <summary>Keeps the backdrop centred on the camera without inheriting its rotation.</summary>
    public class BackdropRider : MonoBehaviour
    {
        public Transform follow;

        void LateUpdate()
        {
            if (follow == null) return;
            transform.position = new Vector3(follow.position.x, 0f, follow.position.z);
        }
    }
}
