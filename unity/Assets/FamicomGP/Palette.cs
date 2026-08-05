using UnityEngine;

namespace FamicomGP
{
    /// <summary>NES-restricted colours and the flat unlit material used for every
    /// surface. Nothing in this game is lit, which is what keeps the look flat.</summary>
    public static class Palette
    {
        public static readonly Color Sky         = Hex("3cbcfc");
        public static readonly Color SkyBand     = Hex("7cd4fc");
        public static readonly Color Grass       = Hex("00a800");
        public static readonly Color GrassDark   = Hex("008c00");
        public static readonly Color Road        = Hex("7c7c7c");
        public static readonly Color RumbleRed   = Hex("d82800");
        public static readonly Color RumbleWhite = Hex("fcfcfc");
        public static readonly Color Line        = Hex("fcfcfc");
        public static readonly Color Ink         = Hex("101010");
        public static readonly Color Mountain    = Hex("5878d8");
        public static readonly Color Snow        = Hex("fcfcfc");
        public static readonly Color Stand       = Hex("2038ec");
        public static readonly Color Hot         = Hex("fcd800");
        public static readonly Color Cool        = Hex("54d8fc");

        public static Color Hex(string rgb)
        {
            Color c;
            ColorUtility.TryParseHtmlString("#" + rgb, out c);
            return c;
        }

        static Shader _opaque;
        static Shader _cutout;

        /// <summary>An unlit material, resolved against whichever render pipeline the
        /// project happens to use.</summary>
        public static Material Flat(Color color)
        {
            if (_opaque == null)
            {
                _opaque = Shader.Find("Universal Render Pipeline/Unlit");
                if (_opaque == null) _opaque = Shader.Find("Unlit/Color");
                if (_opaque == null) _opaque = Shader.Find("Sprites/Default");
            }

            var m = new Material(_opaque);
            if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", color);
            if (m.HasProperty("_Color")) m.SetColor("_Color", color);
            return m;
        }

        public static Shader SpriteShader
        {
            get
            {
                if (_cutout == null) _cutout = Shader.Find("Sprites/Default");
                return _cutout;
            }
        }
    }
}
