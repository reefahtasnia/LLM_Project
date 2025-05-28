import { NextRequest } from "next/server";
import axios from "axios";

export async function POST(request: NextRequest) {
  try {
        const contentType = request.headers.get("content-type") || "";
    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      const file = formData.get("file");
      if (!file || !(file instanceof File)) {
        return new Response(JSON.stringify({ error: "No file uploaded or file is not valid" }), { status: 400 });
      }
      const arrayBuffer = await file.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: file.type });

      // Use form-data to send to Flask
      const fd = new FormData();
      fd.append("file", blob, file.name);

      const uploadRes = await axios.post(
        "http://localhost:5000/upload_pdf",
        fd
      );
      return new Response(JSON.stringify({
        message: uploadRes.data.message,
        filename: uploadRes.data.filename
      }));
    }

    // Handle JSON request for /ask
    const { question } = await request.json();
    const pythonResponse = await axios.post("http://localhost:5000/ask", { question });
    
    // Handle Flask errors
    if (pythonResponse.data.error) {
      return new Response(JSON.stringify({ error: pythonResponse.data.error }));
    }
    
    return new Response(JSON.stringify({ answer: pythonResponse.data.answer }));
    
  } catch (error) {
    return new Response(JSON.stringify({ error: "Failed to process request" }));
  }
}