"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, EyeOff } from "lucide-react";

import { getApiErrorMessage } from "@/lib/errors";
import { getMe, login, register } from "@/lib/api";

type AuthMode = "login" | "register";

function resolveNext(nextParam: string | null): string {
  if (!nextParam) return "/setup/upload";
  if (!nextParam.startsWith("/")) return "/setup/upload";
  return nextParam;
}

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const nextRoute = useMemo(
    () => resolveNext(searchParams.get("next")),
    [searchParams]
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (mode === "register") {
        await register({ email, password });
        setMessage("Account created. Please sign in.");
        setMode("login");
      } else {
        await login({ email, password });
        router.replace(nextRoute);
      }
    } catch (err) {
      setError(getApiErrorMessage(err, "Authentication failed"));
    } finally {
      setLoading(false);
    }
  }

  async function onUseExistingSession() {
    setLoading(true);
    setError(null);
    try {
      await getMe();
      router.replace(nextRoute);
    } catch (err) {
      setError(getApiErrorMessage(err, "No active session found"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 p-6">
      <div className="w-full max-w-md bg-white border rounded-xl p-6 shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">Evalio</h1>
        <p className="text-sm text-gray-600 mb-6">
          {mode === "login" ? "Sign in to continue" : "Create an account"}
        </p>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block">
            <span className="text-sm text-gray-700">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-1 w-full border rounded-md px-3 py-2 text-sm"
              placeholder="you@example.com"
            />
          </label>

          <label className="block">
            <span className="text-sm text-gray-700">Password</span>
            <div className="relative mt-1">
              <input
                type={showPassword ? "text" : "password"}
                required
                minLength={8}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full border rounded-md px-3 py-2 pr-10 text-sm"
                placeholder="At least 8 characters"
              />
              <button
                type="button"
                onClick={() => setShowPassword((value) => !value)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </label>

          {message ? <p className="text-sm text-green-700">{message}</p> : null}
          {error ? <p className="text-sm text-red-700">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-black text-white py-2 text-sm disabled:opacity-60"
          >
            {loading ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <div className="mt-4 flex items-center justify-between text-sm">
          <button
            type="button"
            className="text-gray-700 underline"
            onClick={() => setMode(mode === "login" ? "register" : "login")}
          >
            {mode === "login" ? "Need an account?" : "Already have an account?"}
          </button>
          <button
            type="button"
            className="text-gray-700 underline"
            onClick={onUseExistingSession}
            disabled={loading}
          >
            Use existing session
          </button>
        </div>
      </div>
    </main>
  );
}
