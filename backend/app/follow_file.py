import aiofiles
import asyncio
from pathlib import Path
from typing import AsyncIterator, Callable, Optional


async def follow_file(
    file_path: Path,
    keep_following: Optional[Callable[[], bool]] = None,
    period_seconds: float = 1.0
) -> AsyncIterator[str]:
    """
    Reads a file line-by-line to the end and then waits for new lines
    to be appended and returns those as well. The waiting can be cancelled
    by cancelling the coroutine, which raises asyncio.exceptions.CancelledError
    exception from inside (most likely) the sleep command.

    This cancellation is done automatically by FastApi when the HTTP request
    is cancelled by the client.
    """
    if not file_path.is_file():
        return

    async with aiofiles.open(file_path, "r") as file:
        while True:
            line = await file.readline()
            if line == "": # empty line is "\n", not empty string
                await asyncio.sleep(period_seconds)

                # stop watching if the situation changed
                if keep_following is not None:
                    if not keep_following():
                        return
            else:
                yield line
