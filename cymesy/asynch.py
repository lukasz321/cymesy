import asyncio
from functools import wraps, partial

def async_wrap(func):
    """
    Wrapper.
    """
    from functools import wraps, partial
    import asyncio

    @wraps(func)
    async def run(*args, loop=None, executor=None, **kwargs):
        if loop is None:
            loop = asyncio.get_event_loop()
        pfunc = partial(func, *args, **kwargs)
        return await loop.run_in_executor(executor, pfunc)

    return run

async def run_async(test):
    """
    If I want to perform a bunch of other actions.
    """
    async_test = async_wrap(test)
    result = await async_test(unit, api)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(main())
    # in python3.7 > run this via asyncio.run()

    tests_to_run_async = [
        async_run_test(test1),
        async_run_test(test2),
        async_run_test(test3),
    ]

    await asyncio.gather(*tests_to_run_async)
