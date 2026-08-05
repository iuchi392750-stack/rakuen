using UnityEngine;

namespace FamicomGP
{
    /// <summary>Input read through a guard, so the game still runs (in demo mode) when a
    /// project is configured for the new Input System only and the legacy API throws.</summary>
    public static class Keys
    {
        static bool _legacyBroken;
        static bool _warned;

        public static bool Available { get { return !_legacyBroken; } }

        public static bool Left  { get { return Down(KeyCode.LeftArrow)  || Down(KeyCode.A); } }
        public static bool Right { get { return Down(KeyCode.RightArrow) || Down(KeyCode.D); } }
        public static bool Gas   { get { return Down(KeyCode.UpArrow)    || Down(KeyCode.W) || Down(KeyCode.Z); } }
        public static bool Brake { get { return Down(KeyCode.DownArrow)  || Down(KeyCode.S) || Down(KeyCode.X); } }

        public static bool Start { get { return Pressed(KeyCode.Space) || Pressed(KeyCode.Return); } }
        public static bool Demo  { get { return Pressed(KeyCode.Tab); } }
        public static bool Mute  { get { return Pressed(KeyCode.M); } }

        static bool Down(KeyCode k)
        {
            if (_legacyBroken) return false;
            try { return Input.GetKey(k); }
            catch (System.Exception e) { Complain(e); return false; }
        }

        static bool Pressed(KeyCode k)
        {
            if (_legacyBroken) return false;
            try { return Input.GetKeyDown(k); }
            catch (System.Exception e) { Complain(e); return false; }
        }

        static void Complain(System.Exception e)
        {
            _legacyBroken = true;
            if (_warned) return;
            _warned = true;
            Debug.LogWarning(
                "FamicomGP: keyboard input is unavailable because this project is set to the new " +
                "Input System only. Set Project Settings > Player > Active Input Handling to \"Both\" " +
                "to drive the car. The demo lap will keep running meanwhile. (" + e.GetType().Name + ")");
        }
    }
}
