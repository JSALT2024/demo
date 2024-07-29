import { useCallback, useState } from "react";

interface Slots<T> {
  [key: string]: T;
}

/**
 * It's like the React's useState, just having a "slot" per each video clip
 * and switching between them automatically.
 */
export function useClipState<T>(
  clipIndex: number,
  defaultValue: T,
): [T, (newValue: T) => void] {
  const [allSlots, setAllSlots] = useState<Slots<T>>({});

  const setSlotState = useCallback(
    (newValue: T) => {
      const newAllSlots = {
        ...allSlots,
        [clipIndex]: newValue,
      };
      setAllSlots(newAllSlots);
    },
    [clipIndex, allSlots],
  );

  const slotValue = clipIndex in allSlots ? allSlots[clipIndex] : defaultValue;

  return [slotValue, setSlotState];
}
