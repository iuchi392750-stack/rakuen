using UnityEngine;

namespace FamicomGP
{
    /// <summary>Builds the rear-view car sprites pixel by pixel at runtime, so the
    /// project needs no imported art files. One 24x16 stencil, four liveries.</summary>
    public static class CarArt
    {
        const int Wide = 24;
        const int Tall = 16;

        static readonly string[] Art =
        {
            "....VVVVVVVVVVVVVVVV....",
            "....WWWWWWWWWWWWWWWW....",
            "..........BBBB..........",
            "..........BBBB..........",
            "......BBBBBBBBBBBB......",
            ".....BBBBBBBBBBBBBB.....",
            "KKKK.BBBBBBBBBBBBBB.KKKK",
            "KKKKKBBBBBRRRRBBBBBKKKKK",
            "KKKKKBBBBBRRRRBBBBBKKKKK",
            "KKKKKBBBBBBBBBBBBBBKKKKK",
            "KGGGKBBBBBBBBBBBBBBKGGGK",
            "KGGGK.BBBBBBBBBBBB.KGGGK",
            "KGGGK..BBBBBBBBBB..KGGGK",
            "KKKKK..BBBBBBBBBB..KKKKK",
            ".KKK....BBBBBBBB....KKK.",
            "..K......WWWWWW......K.."
        };

        public struct Livery
        {
            public Color Body;
            public Color Accent;
            public Color Wing;

            public Livery(string body, string accent, string wing)
            {
                Body = Palette.Hex(body);
                Accent = Palette.Hex(accent);
                Wing = Palette.Hex(wing);
            }
        }

        public static readonly Livery Hero   = new Livery("e40010", "fcfcfc", "0038a8");
        public static readonly Livery Yellow = new Livery("fcd800", "181818", "181818");
        public static readonly Livery Green  = new Livery("00a844", "fcfcfc", "fcfcfc");
        public static readonly Livery Orange = new Livery("f87800", "fcfcfc", "fcfcfc");

        public static Sprite Build(Livery livery)
        {
            var tex = new Texture2D(Wide, Tall, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp
            };

            Color tyre = Palette.Hex("181818");
            Color rim = Palette.Hex("9c9c9c");
            Color brake = Palette.Hex("fc5454");
            Color clear = new Color(0f, 0f, 0f, 0f);

            for (int y = 0; y < Tall; y++)
            {
                // texture rows run bottom-up, the stencil top-down
                string row = Art[Tall - 1 - y];
                for (int x = 0; x < Wide; x++)
                {
                    Color c;
                    switch (row[x])
                    {
                        case 'B': c = livery.Body; break;
                        case 'W': c = livery.Accent; break;
                        case 'V': c = livery.Wing; break;
                        case 'K': c = tyre; break;
                        case 'G': c = rim; break;
                        case 'R': c = brake; break;
                        default: c = clear; break;
                    }
                    tex.SetPixel(x, y, c);
                }
            }

            tex.Apply();

            // 6 pixels per unit puts the car at 4 world units wide, just under one lane
            var sprite = Sprite.Create(tex, new Rect(0, 0, Wide, Tall), new Vector2(0.5f, 0f), 6f);
            sprite.name = "Car";
            return sprite;
        }

        public static GameObject Spawn(string name, Livery livery, Transform parent)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Build(livery);
            if (Palette.SpriteShader != null) sr.material = new Material(Palette.SpriteShader);
            return go;
        }
    }
}
