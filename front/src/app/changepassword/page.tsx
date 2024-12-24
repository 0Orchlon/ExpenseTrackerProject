"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { sendRequest, convertToMD5password } from "../../utils/api";

interface Data {
  gmail: string;
  fname: string;
  lname: string;
}
interface Response {
  resultCode: number;
  resultMessage: string;
  data: Data[];
  size: number;
  action: string;
  curdate: string;
}

export default function ChangePassword() {
  const [oldPassword, setOldPassword] = useState<string>("");
  const [newPassword, setNewPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [userInfo, setUserInfo] = useState<Data | null>(null); // Store user info
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      setError("You must be logged in to change your password.");
      return;
    }

    const user = JSON.parse(token);
    setUserInfo(user); // Set user info from local storage (or use the token to fetch)

    setLoading(false);
  }, []);

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    // Validate passwords
    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return;
    }

    if (newPassword.length < 6) {
      setError("New password must be at least 6 characters long.");
      return;
    }

    setLoading(true);

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        setError("You must be logged in to change your password.");
        return;
      }

      const user = JSON.parse(token);
      const hashedOldPassword = convertToMD5password(oldPassword);
      const hashedNewPassword = convertToMD5password(newPassword);

      // Send password change request to the backend
      const surl = "http://localhost:8000/user/";
      const smethod = "POST";
      const sbody = {
        action: "changepassword",
        gmail: user.gmail, // Use the logged-in user's email
        oldpass: hashedOldPassword,
        newpass: hashedNewPassword,
      };

      const response: Response = await sendRequest(surl, smethod, sbody);

      // Handle the response
      if (response.resultCode === 3022) {
        setSuccessMessage(response.resultMessage); // Set the success message from the response
        setOldPassword("");
        setNewPassword("");
        setConfirmPassword("");
        setError("");
      } else {
        setSuccessMessage("");
        setError(response.resultMessage || "Failed to change password.");
      }
    } catch (err) {
      console.error(err);
      setError("An error occurred while changing the password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="text-center text-xl">Loading user info...</p>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-2xl font-bold text-center mb-6 text-black">Change Password</h2>

        {/* Display user info if available */}
        {userInfo && (
          <div className="mb-4 text-center text-black">
            <p>Welcome, {userInfo.fname} {userInfo.lname}!</p>
            <p>Your email: {userInfo.gmail}</p>
          </div>
        )}

        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label
              htmlFor="oldPassword"
              className="block text-sm font-medium text-black"
            >
              Old Password
            </label>
            <input
              type="password"
              id="oldPassword"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Enter your old password"
            />
          </div>

          <div>
            <label
              htmlFor="newPassword"
              className="block text-sm font-medium text-black"
            >
              New Password
            </label>
            <input
              type="password"
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Enter your new password"
            />
          </div>

          <div>
            <label
              htmlFor="confirmPassword"
              className="block text-sm font-medium text-black"
            >
              Confirm New Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Confirm your new password"
            />
          </div>

          {/* Display error or success message */}
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          {successMessage && (
            <p className="text-green-500 text-sm text-center">
              {successMessage}
            </p>
          )}

          <button
            type="submit"
            className="w-full bg-indigo-500 text-white py-2 px-4 rounded-md hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            disabled={loading}
          >
            {loading ? "Changing..." : "Change Password"}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-500 text-center">
          Back to{" "}
          <a href="/dashboard" className="text-indigo-500 hover:underline">
            Dashboard
          </a>
        </p>
      </div>
    </div>
  );
}
