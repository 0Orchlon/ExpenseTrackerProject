import crypto from "crypto";
export const sendRequest = async (
  url: string,
  method: "GET" | "POST" | "PUT" | "DELETE",
  body: Record<string, any> | null = null,
  headers: Record<string, string> = {}
): Promise<any> => {
  try {
    const options: RequestInit = {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
    };

    // Include `body` only for methods that allow it
    if (body && (method === "POST" || method === "PUT")) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (!response.ok) {
      // Attempt to include response details in the error
      const errorBody = await response.text();
      throw new Error(
        `HTTP error! status: ${response.status}, body: ${errorBody}`
      );
    }

    // Handle cases where the response might not be JSON
    try {
      return await response.json();
    } catch {
      return response.text();
    }
  } catch (error) {
    // Enhanced error handling
    if (error instanceof Error) {
      console.error("Error during API request:", error.message); // Log error message
    } else {
      console.error("Error during API request:", error); // Log non-Error object
    }
    throw error; // Re-throw the error for further handling
  }
};

export const convertToMD5password = (password: string): string => {
  return crypto.createHash("md5").update(password).digest("hex");
};
