"use client";

import { useEffect, useRef, useState } from "react";
import { RefreshCcw } from "lucide-react";
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

export default function Fridge() {
  const videoRef = useRef(null);
  const [inventory, setInventory] = useState([]);

  //Captures frame as an image
  const captureFrame = () => {
    if (videoRef.current) {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");
  
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
  
      ctx?.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
  
      const image = canvas.toDataURL("image/jpeg");
      console.log("Frame captured!");
      return image;
    }
    return null;
  };  

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

  const fetchInventory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/inventory");
      if (!res.ok) {
        throw new Error("Failed to fetch inventory");
      }
      const data = await res.json();
      setInventory(data);
    } catch (error) {
      console.error("Error fetching inventory:", error);
    }
  };

  useEffect(() => {
    startCamera()
    fetchInventory()

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

          {/* Inventory Scrollable Card */}
          <div className="w-full max-w-md bg-white shadow-md rounded-xl p-4 border border-gray-200">
          <div className="flex justify-between items-center mb-3">
            <h2 className="text-xl font-semibold text-gray-800">
              Fridge Inventory
            </h2>
            <button 
              onClick={fetchInventory} 
              className="p-2 rounded-full text-gray-600 hover:bg-gray-200 transition"
              aria-label="Refresh Inventory"
            >
              <RefreshCcw className="w-5 h-5" /> {/* Refresh icon */}
            </button>
          </div>

            {/* Scrollable Inner Card */}
            <div className="h-64 overflow-y-scroll rounded-lg border border-gray-100 p-4">
              <ul className="space-y-2">
                {inventory.map((item, index) => (
                  <li 
                    key={index} 
                    className="grid grid-cols-2 gap-4 text-gray-700"
                  >
                    <span className="text-lg text-left">{item.name}</span>
                    <span className="text-lg font-medium text-right">{item.count}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <Stack direction="row" spacing={2}>
            <Button variant="contained" startIcon={<AddIcon />} color="success" sx={{ minWidth: 120 }}>
              Add
            </Button>
            <Button variant="contained" endIcon={<DeleteIcon />} color="error" sx={{ minWidth: 120 }}>
              Delete
            </Button>
          </Stack>

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
