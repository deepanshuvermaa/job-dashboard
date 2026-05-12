"use client";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const [settings, setSettings] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.getSettings()
      .then(setSettings)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await api.updateSettings(settings);
      setMessage("Settings saved successfully");
      setTimeout(() => setMessage(""), 3000);
    } catch (err: any) {
      setMessage(err.message || "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const set = (key: string, value: any) => setSettings((prev: any) => ({ ...prev, [key]: value }));

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-obsidian border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="px-8 py-6 max-w-content mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-heading text-obsidian font-display">Settings</h1>
          <p className="text-body text-gravel mt-1">Manage credentials, API keys, and automation</p>
        </div>
        <button onClick={handleSave} disabled={saving} className="btn-primary disabled:opacity-50">
          {saving ? "Saving..." : "Save Settings"}
        </button>
      </div>

      {message && (
        <div className={`card mb-6 ${message.includes("success") ? "border-grade-a/30" : "border-grade-d/30"}`}>
          <p className="text-caption text-cinder">{message}</p>
        </div>
      )}

      {/* Account */}
      <div className="card mb-6">
        <h2 className="text-body-medium text-obsidian mb-4">Account</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">Name</label>
            <p className="text-body text-cinder">{user?.full_name || "--"}</p>
          </div>
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">Email</label>
            <p className="text-body text-cinder">{user?.email || "--"}</p>
          </div>
        </div>
      </div>

      {/* Credentials */}
      <div className="card mb-6">
        <h2 className="text-body-medium text-obsidian mb-4">Account Credentials</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">LinkedIn Email</label>
            <input
              type="email"
              value={settings.linkedin_email || ""}
              onChange={(e) => set("linkedin_email", e.target.value)}
              className="input-el"
              placeholder="your@email.com"
            />
          </div>
          <div>
            <label className="block text-caption-strong text-obsidian mb-2">GitHub Username</label>
            <input
              type="text"
              value={settings.github_username || ""}
              onChange={(e) => set("github_username", e.target.value)}
              className="input-el"
              placeholder="username"
            />
          </div>
        </div>
      </div>

      {/* API Keys */}
      <div className="card mb-6">
        <h2 className="text-body-medium text-obsidian mb-4">AI API Keys</h2>
        <div className="space-y-4">
          {[
            { key: "openai_api_key", label: "OpenAI API Key", placeholder: "sk-..." },
            { key: "gemini_api_key", label: "Google Gemini API Key", placeholder: "AI..." },
            { key: "anthropic_api_key", label: "Anthropic API Key", placeholder: "sk-ant-..." },
          ].map((field) => (
            <div key={field.key}>
              <label className="block text-caption-strong text-obsidian mb-2">{field.label}</label>
              <input
                type="password"
                value={settings[field.key] || ""}
                onChange={(e) => set(field.key, e.target.value)}
                className="input-el"
                placeholder={field.placeholder}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Automation */}
      <div className="card mb-6">
        <h2 className="text-body-medium text-obsidian mb-4">Automation Settings</h2>
        <div className="space-y-4">
          <label className="flex items-center justify-between p-4 bg-powder rounded-lg cursor-pointer">
            <div>
              <p className="text-body-medium text-obsidian">Auto-Post to LinkedIn</p>
              <p className="text-caption text-gravel">Automatically post approved content to LinkedIn</p>
            </div>
            <input
              type="checkbox"
              checked={settings.auto_post_enabled || false}
              onChange={(e) => set("auto_post_enabled", e.target.checked)}
              className="w-5 h-5 accent-obsidian"
            />
          </label>

          <label className="flex items-center justify-between p-4 bg-powder rounded-lg cursor-pointer">
            <div>
              <p className="text-body-medium text-obsidian">Auto-Apply to Jobs</p>
              <p className="text-caption text-gravel">Automatically apply to jobs that pass the gate criteria</p>
            </div>
            <input
              type="checkbox"
              checked={settings.auto_apply_enabled || false}
              onChange={(e) => set("auto_apply_enabled", e.target.checked)}
              className="w-5 h-5 accent-obsidian"
            />
          </label>

          <div>
            <label className="block text-caption-strong text-obsidian mb-2">Max Applications Per Day</label>
            <input
              type="number"
              value={settings.max_applications_per_day || 50}
              onChange={(e) => set("max_applications_per_day", Number(e.target.value))}
              className="input-el w-40"
              min={1}
              max={200}
            />
            <p className="text-caption text-gravel mt-1">Recommended: 30-50 per day to avoid LinkedIn restrictions</p>
          </div>
        </div>
      </div>

      {/* Danger zone */}
      <div className="card border-grade-d/20">
        <h2 className="text-body-medium text-obsidian mb-4">Account</h2>
        <button onClick={logout} className="text-grade-d text-caption hover:underline">
          Sign Out
        </button>
      </div>
    </div>
  );
}
