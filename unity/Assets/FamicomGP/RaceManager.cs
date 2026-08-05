using UnityEngine;

namespace FamicomGP
{
    /// <summary>Race states, standings, chiptune-ish audio and the on-screen readouts.
    /// Starts in attract mode: the demo driver runs a lap until someone presses Start.</summary>
    public class RaceManager : MonoBehaviour
    {
        public enum Phase { Attract, Countdown, Race, Finish }

        public TrackBuilder track;
        public Racer player;
        public Racer[] rivals;

        public Phase phase = Phase.Attract;
        public float countdown;
        public float elapsed;
        public int resultRank;
        public float? bestTime;

        Racer[] _field;
        AudioSource _engine;
        AudioSource _sfx;
        bool _muted;
        int _lastBeep;

        void Start()
        {
            _field = new Racer[rivals.Length + 1];
            _field[0] = player;
            for (int i = 0; i < rivals.Length; i++) _field[i + 1] = rivals[i];

            BuildAudio();
            EnterAttract();
        }

        // ------------------------------------------------------------------ phases

        void EnterAttract()
        {
            phase = Phase.Attract;
            elapsed = 0f;
            resultRank = 0;
            LineUp();
            player.autoDrive = true;
            foreach (var r in _field) r.Racing = true;
        }

        void EnterCountdown()
        {
            phase = Phase.Countdown;
            countdown = 3.99f;
            elapsed = 0f;
            resultRank = 0;
            _lastBeep = 5;
            LineUp();
            player.autoDrive = false;
            foreach (var r in _field) r.Racing = false;
        }

        void LineUp()
        {
            player.ResetTo(0f, 0f);
            rivals[0].ResetTo(90f, -0.42f);
            rivals[1].ResetTo(150f, 0.34f);
            rivals[2].ResetTo(210f, -0.10f);
        }

        // ------------------------------------------------------------------- frame

        void Update()
        {
            float dt = Mathf.Min(Time.deltaTime, 0.05f);

            if (Keys.Mute) { _muted = !_muted; if (_engine != null) _engine.mute = _muted; }
            if (Keys.Demo && phase != Phase.Countdown) EnterAttract();

            if (Keys.Start)
            {
                if (phase == Phase.Attract || phase == Phase.Finish) EnterCountdown();
            }

            switch (phase)
            {
                case Phase.Countdown:
                    countdown -= dt;
                    int n = Mathf.CeilToInt(countdown);
                    if (n != _lastBeep && n >= 1 && n <= 3) { _lastBeep = n; Blip(440f, 0.12f); }
                    if (countdown <= 0f)
                    {
                        phase = Phase.Race;
                        Blip(880f, 0.3f);
                        foreach (var r in _field) r.Racing = true;
                    }
                    break;

                case Phase.Race:
                    elapsed += dt;
                    if (player.Finished)
                    {
                        phase = Phase.Finish;
                        resultRank = Rank(player);
                        if (resultRank == 1 && (!bestTime.HasValue || elapsed < bestTime.Value))
                            bestTime = elapsed;
                        Fanfare(resultRank == 1);
                    }
                    break;

                case Phase.Attract:
                    if (player.Finished) EnterAttract();
                    break;
            }

            foreach (var r in _field) r.Tick(dt, _field);
            DriveEngine();
        }

        public int Rank(Racer who)
        {
            int ahead = 0;
            foreach (var r in _field)
                if (r != who && r.distance > who.distance) ahead++;
            return ahead + 1;
        }

        // ------------------------------------------------------------------- audio

        void BuildAudio()
        {
            _engine = gameObject.AddComponent<AudioSource>();
            _engine.clip = Tone(70f, 1f, true);
            _engine.loop = true;
            _engine.volume = 0.16f;
            _engine.Play();

            _sfx = gameObject.AddComponent<AudioSource>();
            _sfx.playOnAwake = false;
        }

        void DriveEngine()
        {
            if (_engine == null) return;
            float ratio = player.speed / Mathf.Max(1f, player.maxSpeed);
            _engine.pitch = Mathf.Lerp(_engine.pitch, 0.55f + ratio * 2.1f, 0.15f);
            _engine.volume = _muted ? 0f : Mathf.Lerp(0.07f, 0.2f, ratio);
        }

        void Blip(float freq, float len)
        {
            if (_sfx == null || _muted) return;
            _sfx.PlayOneShot(Tone(freq, len, true), 0.5f);
        }

        void Fanfare(bool won)
        {
            if (_sfx == null || _muted) return;
            if (!won) { _sfx.PlayOneShot(Tone(196f, 0.45f, true), 0.5f); return; }
            StartCoroutine(FanfareRoutine());
        }

        System.Collections.IEnumerator FanfareRoutine()
        {
            float[] notes = { 523f, 659f, 784f, 1047f };
            foreach (float f in notes)
            {
                _sfx.PlayOneShot(Tone(f, 0.18f, true), 0.5f);
                yield return new WaitForSeconds(0.11f);
            }
        }

        /// <summary>A square wave, because that is the sound of the machine being
        /// imitated.</summary>
        static AudioClip Tone(float freq, float seconds, bool square)
        {
            int rate = 44100;
            int frames = Mathf.Max(64, Mathf.RoundToInt(rate * seconds));
            var data = new float[frames];

            for (int i = 0; i < frames; i++)
            {
                float t = i / (float)rate;
                float raw = Mathf.Sin(2f * Mathf.PI * freq * t);
                float v = square ? (raw >= 0f ? 0.45f : -0.45f) : raw;
                float fade = 1f - (i / (float)frames);
                data[i] = v * (square && seconds < 0.6f ? fade : 1f);
            }

            var clip = AudioClip.Create("tone", frames, 1, rate, false);
            clip.SetData(data, 0);
            return clip;
        }

        // --------------------------------------------------------------------- HUD

        void OnGUI()
        {
            float scale = Mathf.Max(1f, Mathf.Floor(Screen.height / 180f));
            Matrix4x4 saved = GUI.matrix;
            GUI.matrix = Matrix4x4.TRS(Vector3.zero, Quaternion.identity, Vector3.one * scale);

            float w = Screen.width / scale;
            var style = new GUIStyle(GUI.skin.label)
            {
                fontSize = 9,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.UpperLeft
            };

            int kmh = Mathf.RoundToInt(player.speed * 2.6f);
            int rank = phase == Phase.Finish ? resultRank : Rank(player);
            int pct = Mathf.RoundToInt(Mathf.Clamp01(player.distance / track.TotalLength) * 100f);

            Label(6, 4, "SPEED " + kmh.ToString("000") + " KM/H", Palette.Hot, style);
            Label(6, 15, "LAP 1/1   " + pct.ToString("000") + "%", Color.white, style);

            style.alignment = TextAnchor.UpperRight;
            Label(w - 106, 4, "POS " + rank + "/4", Color.white, style, 100);
            Label(w - 106, 15, Clock(elapsed), Palette.Cool, style, 100);
            if (bestTime.HasValue) Label(w - 106, 26, "BEST " + Clock(bestTime.Value), new Color(0.72f, 0.72f, 0.8f), style, 100);

            style.alignment = TextAnchor.MiddleCenter;
            float cx = w / 2f - 110f;

            switch (phase)
            {
                case Phase.Attract:
                    Label(cx, 92, "F A M I C O M   G R A N D   P R I X", Palette.Hot, style, 220);
                    Label(cx, 106, "DEMO LAP RUNNING", new Color(0.75f, 0.75f, 0.85f), style, 220);
                    if (Mathf.FloorToInt(Time.time * 2.4f) % 2 == 0)
                        Label(cx, 120, "PRESS SPACE TO RACE", Color.white, style, 220);
                    break;

                case Phase.Countdown:
                    int n = Mathf.CeilToInt(countdown);
                    style.fontSize = 26;
                    Label(cx, 70, n > 0 ? n.ToString() : "GO!", n > 0 ? Color.white : Palette.Hex("00e800"), style, 220);
                    style.fontSize = 9;
                    Label(cx, 108, "YOU START 4TH  -  PASS ALL THREE", new Color(0.8f, 0.8f, 0.9f), style, 220);
                    break;

                case Phase.Finish:
                    bool won = resultRank == 1;
                    style.fontSize = 18;
                    string headline = won ? "1ST PLACE" : resultRank + Suffix(resultRank) + " PLACE";
                    bool flash = Mathf.FloorToInt(Time.time * 4f) % 2 == 0;
                    Label(cx, 74, headline, won && flash ? Palette.Hot : Color.white, style, 220);
                    style.fontSize = 9;
                    if (won) Label(cx, 98, "WINNER!", Palette.Hot, style, 220);
                    Label(cx, 110, "TIME " + Clock(elapsed), Palette.Cool, style, 220);
                    if (flash) Label(cx, 124, "SPACE TO RETRY   TAB FOR DEMO", Color.white, style, 220);
                    break;
            }

            GUI.matrix = saved;
        }

        static void Label(float x, float y, string s, Color c, GUIStyle st, float width = 200f)
        {
            var prev = st.normal.textColor;

            st.normal.textColor = Color.black;
            GUI.Label(new Rect(x + 1, y + 1, width, 30), s, st);

            st.normal.textColor = c;
            GUI.Label(new Rect(x, y, width, 30), s, st);

            st.normal.textColor = prev;
        }

        static string Suffix(int n) { return n == 2 ? "ND" : n == 3 ? "RD" : "TH"; }

        static string Clock(float t)
        {
            int m = (int)(t / 60f);
            int s = (int)(t % 60f);
            int cs = (int)((t * 100f) % 100f);
            return m + ":" + s.ToString("00") + "." + cs.ToString("00");
        }
    }
}
