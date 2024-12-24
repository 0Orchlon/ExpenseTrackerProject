"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { sendRequest } from "../../utils/api";

interface Data {
  uid: number;
  gmail: string;
  fname: string;
  lname: string;
}

export default function EditUser() {
  const [user, setUser] = useState<Data | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");
  const [newFname, setNewFname] = useState<string>("");
  const [newLname, setNewLname] = useState<string>("");
  const router = useRouter();

  useEffect(() => {
    const userData = localStorage.getItem("token");
    if (!userData) {
      router.push("/login");
      return;
    }
  
    try {
      const parsedUser: Data = JSON.parse(userData);
      setUser(parsedUser);
      setNewFname(parsedUser.fname);
      setNewLname(parsedUser.lname);
    } catch (err) {
      console.error("Error parsing user data:", err);
      localStorage.removeItem("token");
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);
  const toDashboard = () => {
    router.push("dashboard")
  }
  const handleSaveChanges = async () => {
    if (newFname === user?.fname && newLname === user?.lname) {
      setSuccessMessage("");
      setError("No changes detected.");
      return;
    }



    try {
      const surl = "http://localhost:8000/useredit/";
      const smethod = "POST";
      const sbody = {
        action: "edituser",
        uid: user?.uid,
        fname: newFname,
        lname: newLname,
      };

      const response = await sendRequest(surl, smethod, sbody);

      if (response.resultCode === 1005) {
        const updatedUser = { ...user, fname: newFname, lname: newLname };
        setUser(updatedUser);
        localStorage.setItem("token", JSON.stringify(updatedUser)); // Update localStorage with new data
        setError("");
        setSuccessMessage("User information updated successfully.");
      } else {
        setSuccessMessage("");
        setError(response.resultMessage);
      }
    } catch (err) {
      console.error(err);
      setSuccessMessage("");
      setError("An error occurred while updating user data.");
    }
  };

  if (loading) return <p className="text-center text-xl">Loading...</p>;

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
        <h1 className="text-3xl font-bold text-center text-black-800 mb-4">
          Error
        </h1>
        <p className="text-lg text-red-600 text-center">User not found.</p>
        <div className="mt-6 flex justify-center">
          <button
            onClick={() => router.push("/login")}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
      <h1 className="text-3xl font-bold text-center text-black mb-4">
        Edit User Info
      </h1>

      <div className="bg-gray-50 p-4 rounded-md shadow-md">
        <h2 className="text-2xl font-semibold text-black">
          Edit your details
        </h2>

        <div className="mt-4">
          <label className="block text-sm font-medium text-black">
            First Name
          </label>
          <input
            type="text"
            value={newFname}
            onChange={(e) => setNewFname(e.target.value)}
            className="mt-2 p-2 w-full border rounded-md text-black"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-black">
            Last Name
          </label>
          <input
            type="text"
            value={newLname}
            onChange={(e) => setNewLname(e.target.value)}
            className="mt-2 p-2 w-full border rounded-md text-black"
          />
        </div>

        {/* Display error or success message */}
        {error && <p className="text-red-500 text-sm text-center">{error}</p>}
        {successMessage && (
          <p className="text-green-500 text-sm text-center">
            {successMessage}
          </p>
        )}

        <div className="mt-6 flex justify-center gap-5">
        <button onClick={toDashboard} 
                className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
            >Back</button>
          <button
            onClick={handleSaveChanges}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
