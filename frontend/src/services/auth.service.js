
const BASE_URL = process.env.NEXT_PUBLIC_API_URL


export async function apiFetch(url, options) {
    let response = await fetch(url, {
        ...options,
        credentials: "include",
    });


    if (response.status === 401) {
        // Don't try to refresh if we're already on login/signup pages
        if (typeof window !== 'undefined') {
            const currentPath = window.location.pathname;
            if (currentPath === '/login' || currentPath === '/signup') {
                throw new Error("Unauthorized");
            }
        }

        const refresh = await fetch(
            `${BASE_URL}/token/refresh/`,
            {
                method: "POST",
                credentials: "include",
            }
        )

        if (!refresh.ok) {
            if (typeof window !== 'undefined') {
                window.location.href = "/login";
            }
            throw new Error("Session expired");
        }

        // Retry original request after refresh
        response = await fetch(url, {
            ...options,
            credentials: "include",
        });
    }

    return response;
}


export async function Register(data) {
    const response = await fetch(`${BASE_URL}/signup/`, {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    if (!response.ok) {
        throw new Error('Could not register user!.')
    }


    return await response.json()
}

export async function Login(data) {
    const response = await fetch(`${BASE_URL}/login/`, {
        method: 'POST',
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })

    if (!response.ok) {
        throw new Error('Could not Login user!.')
    }


    return await response.json()
}
