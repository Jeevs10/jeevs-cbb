"use client";

import { useState, useRef, useEffect } from "react";
import Panel from "@/components/ui/Panel";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { ErrorMessage } from "@/components/ui/ErrorMessage";

interface Prediction {
  width: number;
  height: number;
  x: number;
  y: number;
  confidence: number;
  class: string;
  class_id: number;
  points: Array<{ x: number; y: number }>;
  detection_id: string;
  parent_id: string;
}

interface SegmentationResponse {
  success: boolean;
  result: {
    predictions: Prediction[];
  };
  error: string | null;
}

export default function SegmentationPage() {
  const [image, setImage] = useState<string | null>(null);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setImage(event.target?.result as string);
        setPredictions([]);
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSegment = async () => {
    if (!image) return;

    setLoading(true);
    setError(null);

    try {
      // Convert base64 to file for upload
      const response = await fetch("/api/v1/segmentation", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_data: image.split(",")[1], // Remove data URL prefix
          classes: "person",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: SegmentationResponse = await response.json();

      console.log("API Response:", data);

      if (data.success && data.result) {
        // Handle different response structures
        const preds = data.result.predictions || [];
        if (Array.isArray(preds)) {
          setPredictions(preds);
        } else {
          console.error("Predictions is not an array:", preds);
          setPredictions([]);
        }
      } else {
        throw new Error(data.error || "Segmentation failed");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  // Draw image and bounding boxes on canvas
  useEffect(() => {
    if (!image || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      ctx.drawImage(img, 0, 0);

      // Draw bounding boxes
      if (Array.isArray(predictions)) {
        predictions.forEach((pred) => {
          // Draw bounding box
          ctx.strokeStyle = "#00ff00";
          ctx.lineWidth = 3;
          ctx.strokeRect(pred.x, pred.y, pred.width, pred.height);

          // Draw label with confidence
          ctx.fillStyle = "#00ff00";
          ctx.font = "16px monospace";
          const label = `${pred.class} ${(pred.confidence * 100).toFixed(1)}%`;
          ctx.fillText(label, pred.x, pred.y - 10);

          // Draw segmentation polygon (optional)
          if (pred.points && pred.points.length > 0) {
            ctx.beginPath();
            ctx.moveTo(pred.points[0].x, pred.points[0].y);
            pred.points.forEach((point) => {
              ctx.lineTo(point.x, point.y);
            });
            ctx.closePath();
            ctx.strokeStyle = "rgba(0, 255, 0, 0.5)";
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.fillStyle = "rgba(0, 255, 0, 0.1)";
            ctx.fill();
          }
        });
      }
    };
    img.src = image;
  }, [image, predictions]);

  return (
    <div className="min-h-screen bg-[#E7E8D1]">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-2xl font-bold text-black mb-4 uppercase tracking-wide">
            Image Segmentation
          </h1>
          <p className="text-xs text-black mb-8 max-w-2xl mx-auto">
            Upload an image to detect objects and view bounding boxes with segmentation masks.
          </p>
        </div>

        <Panel className="max-w-4xl mx-auto">
          <div className="space-y-6">
            {/* Upload Section */}
            <div>
              <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
                Upload Image
              </h2>
              <div className="flex gap-4">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] text-xs font-bold text-black uppercase tracking-wide"
                >
                  Select Image
                </button>
                {image && (
                  <button
                    onClick={handleSegment}
                    disabled={loading}
                    className="px-4 py-2 border-2 border-black bg-[#C7D0B8] hover:bg-[#B8C0A8] text-xs font-bold text-black uppercase tracking-wide disabled:opacity-50"
                  >
                    {loading ? "Processing..." : "Segment Image"}
                  </button>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && <ErrorMessage message={error} />}

            {/* Canvas Display */}
            {image && (
              <div>
                <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
                  Results
                </h2>
                <div className="border-2 border-black bg-white">
                  {loading ? (
                    <div className="flex items-center justify-center p-12">
                      <LoadingSpinner />
                    </div>
                  ) : (
                    <canvas
                      ref={canvasRef}
                      className="max-w-full h-auto"
                      style={{ display: "block" }}
                    />
                  )}
                </div>
              </div>
            )}

            {/* Predictions List */}
            {predictions.length > 0 && (
              <div>
                <h2 className="text-xs font-bold text-black mb-4 uppercase tracking-wide border-b-2 border-black pb-2">
                  Detected Objects ({predictions.length})
                </h2>
                <div className="space-y-2">
                  {predictions.map((pred, idx) => (
                    <div
                      key={pred.detection_id}
                      className="flex justify-between items-center p-2 border border-black bg-[#C7D0B8]"
                    >
                      <span className="text-xs font-bold">
                        {idx + 1}. {pred.class}
                      </span>
                      <span className="text-xs">
                        {(pred.confidence * 100).toFixed(1)}% confidence
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Panel>
      </main>
    </div>
  );
}
