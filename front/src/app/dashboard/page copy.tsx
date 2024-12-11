"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { sendRequest } from '@/utils/api'; // Make sure to import the sendRequest function

interface User {
  uid: number;
  gmail: string;
  fname: string;
  lname: string;
  last_login?: string;
}

interface Entry {
  id: number;
  type: string; // 'Income' or 'Expense'
  amount: number;
  date: string;
  category: string;
  description: string;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [income, setIncome] = useState<Entry[]>([]);
  const [expense, setExpense] = useState<Entry[]>([]);
  const [history, setHistory] = useState<Entry[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [newEntry, setNewEntry] = useState<Omit<Entry, "id"> | null>(null);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
    } else {
      try {
        const parsedUser: User = JSON.parse(token);
        setUser(parsedUser);
        fetchData(parsedUser.uid);
      } catch (err) {
        console.error("Invalid token format:", err);
        localStorage.removeItem("token");
        router.push("/login");
      }
    }
  }, [router]);


  const fetchData = async (userId: number) => {
    try {
      // Use the correct URL with the trailing slash
      const incomeData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "allincome",
        uid: userId,
      });
  
      console.log("Income API Response:", incomeData); // Log the full response
  
      if (incomeData.resultCode === 200 && Array.isArray(incomeData.data)) {
        const mappedIncomeData = incomeData.data.map((entry: any, index: number) => ({
          id: index,
          type: "Income",
          amount: entry.income,
          date: new Date(entry.ic_date).toLocaleString(),
          category: entry.ic_type,
          description: entry.ic_type,
        }));
  
        console.log("Mapped income data:", mappedIncomeData); // Log mapped data
        setIncome(mappedIncomeData); // Set income data in state
      } else {
        console.log("No income data or invalid response format");
        setIncome([]); // Set an empty array if no data is found
      }
  
      // Fetch expense data using the correct URL
      const expenseData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "allexpense",
        uid: userId,
      });
  
      console.log("Expense API Response:", expenseData); // Log the full response
  
      if (expenseData.resultCode === 200 && Array.isArray(expenseData.data)) {
        const mappedExpenseData = expenseData.data.map((entry: any, index: number) => ({
          id: index,
          type: "Expense",
          amount: entry.expense,
          date: new Date(entry.ex_date).toLocaleString(),
          category: entry.ex_type,
          description: entry.ex_type,
        }));
  
        console.log("Mapped expense data:", mappedExpenseData); // Log mapped data
        setExpense(mappedExpenseData); // Set expense data in state
      } else {
        console.log("No expense data or invalid response format");
        setExpense([]); // Set an empty array if no data is found
      }
  
      // Fetch history data using the correct URL
      const historyData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "history",
        uid: userId,
      });
  
      setHistory(historyData);
  
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to fetch data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };
  
  
  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return <p className="text-center text-xl">Loading...</p>;
  }

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-4">
          Error
        </h1>
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
      <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
        Dashboard
      </h1>

      <div className="bg-gray-50 p-6 rounded-md shadow-md">
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">
          Welcome, {user.fname} {user.lname}!
        </h2>
        <p className="text-lg text-gray-600">Name: {user.fname} {user.lname}</p>
        <div className="mt-4 space-x-4">
          <button
            onClick={() => router.push("/changepassword")}
            className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition"
          >
            Change Password
          </button>
          <button
            onClick={() => router.push("/edituser")}
            className="bg-gray-300 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-400 transition"
          >
            Edit Profile
          </button>
          <div className="mt-6 flex justify-center">
        <button
          onClick={handleLogout}
          className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
        >
          Logout
        </button>
      </div>
        </div>
      </div>

      <div className="mt-6">
        <h2 className="text-xl font-semibold text-gray-800">Income</h2>
        <table >
            <tr className="tx-l font-sans text-black">
              <th>Expense</th>
              <th>Description</th>
              <th>Date</th>
            </tr>
            {income.length > 0 ? (
              income.map((entry) => (
            <tr key={entry.id} className="tx-l font-sans text-black">
              <td>+{entry.amount}$</td>
              <td>{entry.description} </td>
              <td>{entry.date}</td>
              
            </tr>
            ))
          ) : (
            <p>No Income data available</p>
          )}
        </table>
      </div>

      <div className="mt-6">
        <h2 className="text-xl font-semibold text-gray-800">Expense</h2>          
        <table >
            <tr className="tx-l font-sans text-black">
              <th>Expense</th>
              <th>Description</th>
              <th>Date</th>
            </tr>
            {expense.length > 0 ? (
              expense.map((entry) => (
            <tr key={entry.id} className="tx-l font-sans text-black">
              <td>{entry.amount}$</td>
              <td>{entry.description} </td>
              <td>{entry.date}</td>
              
            </tr>
            ))
          ) : (
            <p>No expense data available</p>
          )}
        </table>
      </div>
    </div>
  );
}
