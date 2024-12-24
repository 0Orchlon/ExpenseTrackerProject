"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link"; // Use next/link for better routing
import { sendRequest, convertToMD5password } from "../../utils/api";

interface Data {
  uid: number;
  gmail: string;
  lname: string;
  fname: string;
  lastlogin: string;
}

interface Response {
  resultCode: number;
  resultMessage: string;
  data: Data[];
  size: number;
  action: string;
  curdate: string;
}

export default function Login() {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Check if the user is already logged in and redirect
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/dashboard");
    } else {
      setLoading(false);
    }
  }, [router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const hashedPassword = convertToMD5password(password);

      const surl = "http://localhost:8000/user/";
      const smethod = "POST";
      const sbody = {
        action: "login",
        gmail: email,
        password: hashedPassword,
      };

      const response: Response = await sendRequest(surl, smethod, sbody);

      if (response.resultCode === 1002 && response.data?.length) {
        const userData = response.data[0];
        localStorage.setItem("token", JSON.stringify(userData));
        router.push("/dashboard");
      } else {
        setError(response.resultMessage || "Login failed. Please try again.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "An error occurred. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="text-center text-xl">Loading...</p>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6 text-black">
        <h2 className="text-2xl font-bold text-center mb-6">
          Login to Your Account
        </h2>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-black"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Enter your email"
            />
          </div>
          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-black"
            >
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Enter your password"
            />
          </div>
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <button
            type="submit"
            className={`w-full py-2 px-4 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-400 ${
              loading
                ? "bg-indigo-300 cursor-not-allowed"
                : "bg-indigo-500 text-white hover:bg-indigo-600"
            }`}
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="mt-4 text-sm text-black text-center">
          Don't have an account?{" "}
          <Link href="/register" className="text-indigo-500 hover:underline">
            Sign up
          </Link>
        </p>

        <p className="mt-2 text-sm text-black text-center">
          Forgot your password?{" "}
          <Link href="/forgot" className="text-indigo-500 hover:underline">
            Reset it here
          </Link>
        </p>
      </div>
    </div>
  );
}
