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
  description: string;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [history, setHistory] = useState<Entry[]>([]);
  const [incomesum, setIncome] = useState<number>(0);
  const [expensesum, setExpense] = useState<number>(0);
  const [totalsum, setTotal] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [amount, setAmount] = useState<number>(0); // Price input
  const [description, setDescription] = useState<string>(''); // Description input
  const [type, setType] = useState<string>('Income'); // Type dropdown (Income or Expense)
  
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
      // Fetch history data
      const historyData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "history",
        uid: userId,
      });
      const incomesumData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "incomesum",
        uid: userId
      });
      const expenseData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "expensesum",
        uid: userId
      });
      const totalSumData = await sendRequest("http://localhost:8000/user/", "POST", {
        action: "total",
        uid: userId
      });

      const mappedHistoryData = historyData.data.map((entry: any, index: number) => ({
        id: index,
        type: entry.type,
        amount: entry.expense,
        date: new Date(entry.date).toLocaleString(),
        description: entry.desc,
      }));

      const totalIncome = incomesumData.data[0]?.totalIncome || 0;
      setIncome(totalIncome);

      const totalExpense = parseFloat(expenseData.data[0]?.totalIncome || expenseData.data[0]?.totalExpense || "0");
      setExpense(isNaN(totalExpense) ? 0 : totalExpense);

      const totalSum = parseFloat(totalSumData.data[0]?.total || "0");
      setTotal(isNaN(totalSum) ? 0 : totalSum);

      setHistory(mappedHistoryData);
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
  
const toIncome = () => {
  router.push("/income")
}  

const toExpense = () => {
  router.push("/expense")
}

  const handleSubmit = async () => {
    if (amount <= 0 || !description) {
      alert("Please provide a valid amount and description");
      return;
    }

    const action = type === "Income" ? "logincome" : "addexpense";

    try {
      const response = await sendRequest("http://localhost:8000/user/", "POST", {
        action,
        uid: user?.uid,
        amount,
        description,
      });
      console.log("Response from server:", response);
      fetchData(user!.uid); // Refresh the data after submission
    } catch (err) {
      console.error("Error submitting entry:", err);
      setError("Failed to submit data. Please try again.");
    }
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
    <>
      <div className="max-w-3xl mx-auto p-6 bg-white rounded-lg shadow-lg mt-8">
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-6">
          Dashboard
        </h1>

        <div className="bg-gray-50 p-6 rounded-md shadow-md">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">
            Welcome, {user.fname} {user.lname}!
          </h2>
          
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
            <button
              onClick={handleLogout}
              className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
            >
              Logout
            </button>
          </div>
        </div>

    <div className="flex justify-normal">
      <div className="py-5 px-5 flex justify-normal shadow-md rounded-md mt-6 p-6">
      <button onClick={toIncome} 
          className="bg-green-900 text-white px-6  py-2 rounded-md hover:bg-indigo-700 transition">
        Incomes</button>
      <p className=" px-6 py-2 rounded-md"></p>
      <button onClick={toExpense}
       className="bg-red-900 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition">
        Expenses</button>
      </div>
    </div>
        <div className="mt-6 bg-gray-50 p-6 rounded-md shadow-md text-black">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Add New Entry</h3>
          <div className="flex flex-col space-y-4">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Number(e.target.value))}
              placeholder="Amount"
              className="px-4 py-2 border rounded-md"
            />
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description"
              className="px-4 py-2 border rounded-md"
            />
            <select
              value={type}
              onChange={(e) => setType(e.target.value)}
              className="px-4 py-2 border rounded-md"
            >
              <option value="Income">Income</option>
              <option value="Expense">Expense</option>
            </select>
            <button
              onClick={handleSubmit}
              className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition"
            >
              Submit
            </button>
          </div>
        </div>

        <h2 className="text-xl font-semibold text-gray-800 mt-8 justify-center">History</h2>
        <div className="flex 2xl:w-6/12">
          <div className="text-green-500 justify-start px-10">
            <h3>Total Income</h3>
            <h3>{incomesum}$</h3>
          </div>
          <div className="text-blue-500 justify-center px-40">
            <br />
            <h3>Total</h3>
            <h3>{totalsum}</h3>
          </div>
          <div className="text-red-500 justify-end px-10">
            <h3>Total Expense</h3>
            <h3>{expensesum}$</h3>
          </div>
        </div>

        <table className="w-full mt-4">
          <thead>
            <tr className="text-left font-semibold text-gray-700">
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Amount</th>
              <th className="px-4 py-2">Description</th>
              <th className="px-4 py-2">Date</th>
            </tr>
          </thead>
          <tbody>
            {history.length > 0 ? (
              history.map((entry) => (
                <tr key={entry.id} className="border-b text-black">
                  <td className="px-4 py-2">{entry.type}</td>
                  <td className="px-4 py-2">{entry.amount < 0 ? `-${Math.abs(entry.amount)}$` : `+${entry.amount}$`}</td>
                  <td className="px-4 py-2">{entry.description}</td>
                  <td className="px-4 py-2">{entry.date}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="px-4 py-2 text-center text-gray-500">
                  No history data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
