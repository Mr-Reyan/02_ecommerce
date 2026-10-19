import { NextResponse } from "next/server";

export function proxy(request){
    const token = request.cookies.get('access')
    
    const isAuthPage =
        request.nextUrl.pathname === "/login" ||
        request.nextUrl.pathname === "/signup";
    
    
    if(!token && !isAuthPage){
        return NextResponse.redirect(
            new URL('/login',request.url)
        )
    }

    if(token && isAuthPage){
        return NextResponse.redirect(
            new URL('/',request.url)
        )
    }

    return NextResponse.next()
}

export const config = {
    matcher: [
        "/cart",
        "/orders",
        "/login",
        "/signup",
    ]
}