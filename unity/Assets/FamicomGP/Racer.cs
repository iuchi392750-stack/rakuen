using UnityEngine;

namespace FamicomGP
{
    /// <summary>
    /// A car on the circuit. Movement is arcade-style: a distance along the centreline
    /// plus a lateral offset, never a physics body — which is what makes it feel like the
    /// era it is imitating. Drives itself in demo mode and for every rival.
    /// </summary>
    public class Racer : MonoBehaviour
    {
        public enum Mode { Player, Rival }

        public Mode mode = Mode.Player;
        public TrackBuilder track;
        public Transform lookAt;          // camera, for billboarding

        public float distance;
        public float lateral;             // -1 = left edge, +1 = right edge
        public float speed;

        public float maxSpeed = 118f;
        public float accel = 34f;
        public float brakePower = 96f;
        public float coast = 16f;
        public float steerRate = 1.35f;

        [Header("Rival / demo driving")]
        public float targetLane;
        public float wobble = 1f;
        public bool autoDrive;

        public bool Racing { get; set; }
        public bool Finished { get; private set; }

        SpriteRenderer _sprite;
        float _wobblePhase;
        float _bounce;

        void Awake()
        {
            _sprite = GetComponentInChildren<SpriteRenderer>();
            _wobblePhase = Random.value * 10f;
        }

        // ------------------------------------------------------------------ frame

        public void Tick(float dt, Racer[] field)
        {
            if (!Racing)
            {
                Face();
                Place();
                return;
            }

            if (mode == Mode.Rival) DriveRival(dt);
            else if (autoDrive) DriveDemo(dt, field);
            else DrivePlayer(dt);

            ApplyCurve(dt);
            Avoid(dt, field);

            speed = Mathf.Clamp(speed, 0f, maxSpeed * 1.02f);
            distance += speed * dt;
            lateral = Mathf.Clamp(lateral, -2.4f, 2.4f);

            if (distance >= track.TotalLength)
            {
                distance = track.TotalLength;
                Finished = true;
            }

            _bounce = Mathf.Sin(Time.time * 26f) * 0.05f * (speed / maxSpeed);
            Face();
            Place();
        }

        // ------------------------------------------------------------------ input

        void DrivePlayer(float dt)
        {
            float steer = 0f;
            if (Keys.Left) steer -= 1f;
            if (Keys.Right) steer += 1f;

            lateral += steer * steerRate * dt * Mathf.Clamp01(speed / (maxSpeed * 0.35f));

            if (Keys.Gas) speed += accel * dt;
            else if (Keys.Brake) speed -= brakePower * dt;
            else speed -= coast * dt;
        }

        /// <summary>Attract-mode driver. Reads the curve ahead, lifts for the tight ones
        /// and takes a tidy line, so a recording of it looks like someone playing.</summary>
        void DriveDemo(float dt, Racer[] field)
        {
            float ahead = CurveAhead(60f);
            float tight = Mathf.Abs(ahead);

            // aim into the corner rather than fighting it
            float aim = Mathf.Clamp(-ahead * 0.055f, -0.65f, 0.65f);

            // pull out to pass anything close in front
            foreach (var r in field)
            {
                if (r == this) continue;
                float gap = r.distance - distance;
                if (gap > 0f && gap < 42f && Mathf.Abs(r.lateral - lateral) < 0.5f)
                    aim = r.lateral > 0f ? r.lateral - 0.72f : r.lateral + 0.72f;
            }

            lateral = Mathf.MoveTowards(lateral, Mathf.Clamp(aim, -0.85f, 0.85f), steerRate * 0.9f * dt);

            float wanted = maxSpeed * Mathf.Lerp(1f, 0.72f, Mathf.Clamp01(tight / 9f));
            speed = Mathf.MoveTowards(speed, wanted, (speed < wanted ? accel : brakePower * 0.5f) * dt);
        }

        void DriveRival(float dt)
        {
            _wobblePhase += dt * wobble * 0.5f;
            float want = targetLane + Mathf.Sin(_wobblePhase) * 0.14f;
            lateral = Mathf.MoveTowards(lateral, want, steerRate * 0.55f * dt);
            speed = Mathf.MoveTowards(speed, maxSpeed, accel * dt);
        }

        // ----------------------------------------------------------------- physics

        void ApplyCurve(float dt)
        {
            // centrifugal drift: the faster you take a corner, the wider it pushes you
            float curve = CurveAhead(10f);
            lateral += curve * 0.024f * (speed / maxSpeed) * dt;

            if (Mathf.Abs(lateral) > 1f && speed > maxSpeed * 0.25f)
                speed -= maxSpeed * 0.55f * dt;
        }

        void Avoid(float dt, Racer[] field)
        {
            foreach (var r in field)
            {
                if (r == this) continue;
                float gap = r.distance - distance;
                if (gap <= 0f || gap > 7f) continue;
                if (Mathf.Abs(r.lateral - lateral) > 0.42f) continue;

                speed = Mathf.Min(speed, r.speed * 0.88f);
                lateral += (lateral < r.lateral ? -1f : 1f) * dt * 1.5f;
            }
        }

        /// <summary>Signed heading change over the next `metres`, in degrees.</summary>
        public float CurveAhead(float metres)
        {
            int i = Mathf.Clamp(Mathf.FloorToInt(distance / TrackBuilder.SegmentLength), 0, track.Center.Count - 2);
            int j = Mathf.Clamp(i + Mathf.RoundToInt(metres / TrackBuilder.SegmentLength), 0, track.Center.Count - 2);
            return Vector3.SignedAngle(track.Forward(i), track.Forward(j), Vector3.up);
        }

        void Place()
        {
            Vector3 p = track.PointAt(distance, lateral);
            p.y += _bounce;
            transform.position = p;
        }

        void Face()
        {
            if (_sprite == null || lookAt == null) return;
            Vector3 dir = lookAt.position - transform.position;
            dir.y = 0f;
            if (dir.sqrMagnitude > 0.0001f)
                _sprite.transform.rotation = Quaternion.LookRotation(dir.normalized, Vector3.up);
        }

        public void ResetTo(float dist, float lane)
        {
            distance = dist;
            lateral = lane;
            targetLane = lane;
            speed = 0f;
            Finished = false;
            Racing = false;
            Place();
        }
    }
}
