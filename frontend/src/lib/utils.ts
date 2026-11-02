import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const LETTERS = ["A", "B", "C", "D", "E", "F"];

export const pct = (x: number) => `${Math.round(x * 100)} %`;

export const num = (x: number) => x.toLocaleString("es-CL");

/** Achica una foto a JPEG de 768 px de lado para no mandar megas a la API. */
export function fileToDataUrl(file: File, side = 768): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const scale = Math.min(1, side / Math.max(img.width, img.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext("2d")!.drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(img.src);
      resolve(canvas.toDataURL("image/jpeg", 0.85));
    };
    img.onerror = () => reject(new Error("No se pudo leer la imagen."));
    img.src = URL.createObjectURL(file);
  });
}
