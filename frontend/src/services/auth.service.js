
const BASE_URL = process.env.NEXT_PUBLIC_API_URL


function getCookie(name) {
    const cookies = document.cookie.split("; ");

    const cookie = cookies.find((row) =>
        row.startsWith(`${name}=`)
    );

    return cookie?.split("=")[1];
}


export async function apiFetch(url, options) {
    let response = await fetch(url, {
        ...options,
        credentials: "include",
    });


    if (response.status === 401) {
        const refresh = await fetch(
            `${BASE_URL}/token/refresh/`,
            {
                method: "POST",
                credentials: "include",
            }
        )

        if (!refresh.ok) {
            window.location.href = "/login";
            throw new Error("Session expired");
        }


        const csrfToken = getCookie("csrftoken");

        const headers = new Headers(options.headers);
        console.log(headers)
        if (csrfToken) {
            headers.set("X-CSRFToken", csrfToken);
        }


        response = await fetch(url, {
            ...options,
            headers,
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
