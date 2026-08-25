"use client";

import React, { useState, useCallback, useRef, useEffect } from "react";
import { debounce, DEBOUNCE_DELAY } from "@/lib/utils";

interface PlayerSearchProps {
  value: string;
  onChange: (value: string) => void;
  onEnter?: () => void;
  placeholder?: string;
  disabled?: boolean;
}

export const PlayerSearch = React.memo(function PlayerSearch({
  value,
  onChange,
  onEnter,
  placeholder = "Search players or teams...",
  disabled = false
}: PlayerSearchProps) {
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);
  const isTypingRef = useRef(false);

  const debouncedOnChange = useCallback(
    debounce((newValue: string) => {
      onChange(newValue);
      isTypingRef.current = false;
    }, DEBOUNCE_DELAY),
    [onChange]
  );

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    isTypingRef.current = true;
    setLocalValue(newValue);
    debouncedOnChange(newValue);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && onEnter) {
      onEnter();
    }
  };

  useEffect(() => {
    if (!isTypingRef.current) {
      setLocalValue(value);
    }
  }, [value]);

  return (
    <div className="mb-3">
      <input
        ref={inputRef}
        type="text"
        placeholder={placeholder}
        value={localValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className="
          w-full max-w-sm
          border-2 border-black
          bg-[#E7E8D1]
          px-3 py-2
          text-xs
          outline-none
          shadow-[3px_3px_0px_black]
          disabled:opacity-50
          disabled:cursor-not-allowed
        "
      />
    </div>
  );
});
