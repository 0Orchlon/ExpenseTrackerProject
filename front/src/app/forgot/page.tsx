"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { sendRequest } from "../../utils/api";

interface Data {
  gmail: string;
}
interface Response {
  resultCode: number;
  resultMessage: string;
  data: Data[];
  size: number;
  action: string;
  curdate: string;
}

export default function ForgotPassword() {
  const [email, setEmail] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [loadingSendLink, setLoadingSendLink] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true); // Add state to check login status
  const [isFormSubmitted, setIsFormSubmitted] = useState<boolean>(false); // Track if form is submitted
  const router = useRouter();

  // Check if the user is logged in
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // If user is logged in, redirect to the dashboard
      router.push("/dashboard");
    } else {
      setLoading(false); // If not logged in, allow access to forgot password page
    }
  }, [router]);

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate input
    if (!email) {
      setError("Please enter your email.");
      return;
    }

    // Simple email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoadingSendLink(true);
    try {
      // Make a request to the backend to send password reset email
      let surl = "http://localhost:8000/user/";
      let smethod = "POST";
      let sbody = {
        action: "forgot",
        gmail: email,
      };

      const response: Response = await sendRequest(surl, smethod, sbody);

      // Handle the response based on resultCode
      if (response.resultCode === 3012) {
        setSuccessMessage(response.resultMessage);
        setError(""); // Clear any previous error
        setIsFormSubmitted(true); // Disable form on successful submission
      } else {
        setSuccessMessage(""); // Clear success message on error
        setError(response.resultMessage);
      }
    } catch (err) {
      console.log(err);
      setError(
        "An error occurred while trying to send the reset email. Please try again."
      );
    } finally {
      setLoadingSendLink(false);
    }
  };

  // Show loading message while checking if user is logged in
  if (loading) return <p className="text-center text-xl">Loading...</p>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
        <h2 className="text-2xl font-bold text-center mb-6">Forgot Password</h2>

        {/* Form starts */}
        <form onSubmit={handleForgotPassword} className="space-y-4">
          <div>
            <label
              htmlFor="email"
              className="block text-sm font-medium text-gray-700"
            >
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isFormSubmitted} // Disable input after successful submission
              className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Enter your email"
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
            disabled={loadingSendLink || isFormSubmitted} // Disable button on success or while sending
          >
            {loadingSendLink ? "Sending..." : "Send Reset Link"}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-500 text-center">
          Remember your password?{" "}
          <a href="/login" className="text-indigo-500 hover:underline">
            Login here
          </a>
        </p>
      </div>
    </div>
  );
}
