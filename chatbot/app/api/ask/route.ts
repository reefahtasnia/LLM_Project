import { NextRequest } from "next/server";
import axios from "axios";

export async function POST(request: NextRequest) {
  try {
    const { question } = await request.json();
    const pythonResponse = await axios.post("http://localhost:5000/ask", { question });
    
    // Handle Flask errors
    if (pythonResponse.data.error) {
      return new Response(JSON.stringify({ error: pythonResponse.data.error }));
    }
    
    return new Response(JSON.stringify({ answer: pythonResponse.data.answer }));
    
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to get answer" }));
  }
}