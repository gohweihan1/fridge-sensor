"use client";

import { useEffect, useRef, useState } from "react";

export default function Fridge() {
  const videoRef = useRef(null);
  const [isInput, setIsInput] = useState(true);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user" }, // "user" uses the front camera
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Error accessing camera:", error);
      }
    };

    startCamera();
  }, []);

  return (
    <div className="min-h-screen bg-emerald-50 flex items-center justify-center p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl w-full">
        {/* Left Column - Text & Future Features */}
        <div className="flex flex-col justify-center space-y-6 p-6">
          <h1 className="text-3xl font-bold text-gray-800">Welcome inside the fridge</h1>
          <p className="text-lg text-gray-600">
            This page mimics a fridge sensor, where inventory items are scanned and either added or removed from the fridge's inventory.
          </p>
          <ul className="list-disc list-inside text-gray-700">
            <li>🔍 Llama vision model used to identify inventory objects in frame</li>
            <li>📋 View real-time inventory.</li>
            <li>🔔 Get expiration reminders.</li>
          </ul>
          <p className="text-md text-gray-500">
            Stay tuned for more features!
          </p>
        </div>

        {/* Right Column - Camera Feed */}
        <div className="flex items-center justify-center">
          <div className="relative w-full max-w-2xl aspect-[16/9] bg-black rounded-xl overflow-hidden shadow-2xl">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
