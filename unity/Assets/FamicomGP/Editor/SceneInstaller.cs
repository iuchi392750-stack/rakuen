#if UNITY_EDITOR
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FamicomGP.EditorTools
{
    /// <summary>
    /// Creates and opens the race scene the first time the project is loaded, and puts it
    /// in the build settings — so the project is playable straight after opening without
    /// anyone building a scene by hand. Unity authors the scene file itself, which keeps
    /// every asset reference valid.
    /// </summary>
    [InitializeOnLoad]
    public static class SceneInstaller
    {
        const string SceneDir = "Assets/Scenes";
        const string ScenePath = SceneDir + "/Race.unity";
        const string DoneKey = "FamicomGP.SceneInstalled";

        static SceneInstaller()
        {
            // wait for the import pipeline to settle before touching scenes
            EditorApplication.delayCall += Install;
        }

        static void Install()
        {
            if (Application.isPlaying) return;
            if (File.Exists(ScenePath))
            {
                Register();
                return;
            }
            if (SessionState.GetBool(DoneKey, false)) return;
            SessionState.SetBool(DoneKey, true);

            if (!Directory.Exists(SceneDir)) Directory.CreateDirectory(SceneDir);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("FamicomGP");
            go.AddComponent<GameBootstrap>();

            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene, ScenePath);
            AssetDatabase.Refresh();

            Register();
            Debug.Log("FamicomGP: created " + ScenePath + ". Press Play to race.");
        }

        static void Register()
        {
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            foreach (var s in scenes)
                if (s.path == ScenePath) return;

            scenes.Insert(0, new EditorBuildSettingsScene(ScenePath, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        [MenuItem("Famicom GP/Open Race Scene")]
        static void OpenScene()
        {
            if (!File.Exists(ScenePath))
            {
                SessionState.SetBool(DoneKey, false);
                Install();
                return;
            }
            EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo();
            EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
        }

        [MenuItem("Famicom GP/Play Now")]
        static void PlayNow()
        {
            if (!EditorApplication.isPlaying)
            {
                OpenScene();
                EditorApplication.isPlaying = true;
            }
        }
    }
}
#endif
