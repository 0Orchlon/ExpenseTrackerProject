"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { sendRequest, convertToMD5password } from "../../../utils/api";

export default function ResetPassword() {
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const router = useRouter();
  const token = new URLSearchParams(window.location.search).get("token");

  const handleSubmit = async () => {
    if (!token) {
      setError("Invalid or missing token.");
      return;
    }

    if (!password || !confirmPassword) {
      setError("Both fields are required.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const hashedPassword = convertToMD5password(password);
      const response = await sendRequest(
        "http://localhost:8000/user/",
        "POST",
        {
          action: "resetpassword",
          token: token,
          newpass: hashedPassword,
        }
      );

      if (response.resultCode === 200) {
        setSuccessMessage("Password reset successfully! Redirecting to login...");
        setError(null);
        setTimeout(() => router.push("/login"), 3000); // Redirect after success
      } else if (response.resultCode === 3019) {
        setSuccessMessage("Password reset successfully! Redirecting to login...");
        setError(null);
        router.push("/login"); // Redirect immediately for this code
      } else {
        setError(response.resultMessage || "Failed to reset password.");
        setSuccessMessage(null);
      }
    } catch (err) {
      console.error(err);
      setError("An error occurred while resetting the password.");
      setSuccessMessage(null);
    }
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
      <h1 className="text-2xl font-bold text-center text-black mb-6">
        Reset Password
      </h1>

      {error && <p className="text-red-600 text-center mb-4">{error}</p>}
      {successMessage && <p className="text-green-600 text-center mb-4">{successMessage}</p>}

      <div className="space-y-4">
        <div>
          <label htmlFor="password" className="block text-black font-medium">
            New Password
          </label>
          <input
            type="password"
            id="password"
            className="w-full text-black p-2 border rounded-md"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="confirmPassword" className="block text-black font-medium">
            Confirm Password
          </label>
          <input
            type="password"
            id="confirmPassword"
            className="w-full text-black p-2 border rounded-md"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
        </div>
        <button
          onClick={handleSubmit}
          className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition"
        >
          Reset Password
        </button>
      </div>
    </div>
  );
}
