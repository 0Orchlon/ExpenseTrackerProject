"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { sendRequest } from "@/utils/api";

interface User {
  uid: number;
  gmail: string;
  fname: string;
  lname: string;
  last_login?: string;
}

interface Entry {
  id: number;
  amount: number;
  date: string;
  description: string;
}

export default function Expenses() {
  const [user, setUser] = useState<User | null>(null);
  const [history, setHistory] = useState<Entry[]>([]);
  const [expensesum, setEXpenseSmum] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const parsedUser: User = JSON.parse(token);
      setUser(parsedUser);
      fetchData(parsedUser.uid);
    } catch (err) {
      console.error("Invalid token format:", err);
      localStorage.removeItem("token");
      router.push("/login");
    }
  }, [router]);

  const fetchData = async (userId: number) => {
    try {
      setLoading(true);

      const historyData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "allexpense",
        uid: userId,
      });

      const expensesumData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "expensesum",
        uid: userId,
      });

      // Map and set the fetched data
      const totalExpense = expensesumData?.data?.[0]?.totalExpense ?? 0; // Default to 0 if value is not present
      setEXpenseSmum(totalExpense);

      
      
      const formattedHistory = historyData.data.map((entry: any, index: number) => ({
        id: index,
        amount: entry.expense,
        date: new Date(entry.ex_date).toLocaleString(),
        description: entry.ex_type,
      }));

      setHistory(formattedHistory);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to fetch data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  const toDashboard = () => {
    router.push("dashboard")
  }
  
  if (loading) {
    return <p className="text-center text-xl">Loading...</p>;
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-4">Error</h1>
        <p className="text-lg text-red-600 text-center">{error}</p>
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleLogout}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-4">Error</h1>
        <p className="text-lg text-red-600 text-center">User not found.</p>
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleLogout}
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
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">Income History</h1>
      <div className="bg-gray-50 p-6 rounded-md shadow-md">
        <div>
            <button onClick={toDashboard} 
                className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
            >Back</button>
        </div>
        <p className="text-lg text-gray-600">Total Income: ${expensesum}</p>
      </div>

      <div className="mt-6 bg-gray-50 p-6 rounded-md shadow-md">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">History</h3>
        <table className="w-full mt-4 text-black">
          <thead>
            <tr className="text-left font-semibold text-gray-700">
              <th className="px-4 py-2">Amount</th>
              <th className="px-4 py-2">Description</th>
              <th className="px-4 py-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {history.length > 0 ? (
              history.map((entry) => (
                <tr key={entry.id} className="border-b">
                  <td className="px-4 py-2">
                    {entry.amount < 0
                      ? `-${Math.abs(entry.amount)}$`
                      : `+${entry.amount}$`}
                  </td>
                  <td className="px-4 py-2">{entry.description}</td>
                  <td className="px-4 py-2">{entry.date}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={3} className="px-4 py-2 text-center text-gray-500">
                  No history data available.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
