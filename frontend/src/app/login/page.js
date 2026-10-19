'use client';
import { loginSchema } from '@/lib/validations/auth.schema'
import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Login } from '@/services/auth.service';
import { Eye,  EyeOff, Loader2 } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useState } from 'react';

const LoginPage = () => {
    const [seePass, setSeePass] = useState(false)
    const router = useRouter()
    
    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting }
    } = useForm({
        resolver: zodResolver(loginSchema)
    })

    const onSubmit = async (data) => {

        try {
            await Login(data);
            toast.success("Logged In!")
            router.back()

        } catch (error) {
            toast.error("Invalid email or password.");
        }
    }

    return (
        <Card className="w-full max-w-md shadow-xl border-0 mx-auto mt-30">
            <CardHeader className="space-y-2 text-center">
                <CardTitle className="text-3xl font-bold">
                    Welcome Back
                </CardTitle>

                <CardDescription>
                    Sign in to get premium clothing.
                </CardDescription>
            </CardHeader>

            <CardContent>
                <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
                    <div className="space-y-2">
                        <Label>Username</Label>

                        <Input
                            {...register('username')}
                            type='text'
                            placeholder="jhon_doe"
                        />
                        {errors.username && (
                            <p className="text-red-500">{errors.username.message}</p>
                        )}
                    </div>

                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <Label>Password</Label>

                            <Link
                                href="/reset-password"
                                className="text-sm text-primary hover:underline"
                            >
                                Forgot password?
                            </Link>
                        </div>

                        <div className="relative">
                            <Input
                                {...register("password")}
                                type={seePass ? "text" : "password"}
                                placeholder="••••••••"
                                className="pr-10"
                            />

                            <button
                                type="button"
                                onClick={() => setSeePass(!seePass)}
                                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                            >
                                {seePass ? (
                                    <EyeOff className="h-4 w-4" />
                                ) : (
                                    <Eye className="h-4 w-4" />
                                )}
                            </button>
                        </div>

                        {errors.password && (
                            <p className="text-red-500">{errors.password.message}</p>
                        )}
                    </div>

                    <Button className="w-full" type="submit">
                        {isSubmitting ? <Loader2 className='animate-spin' /> : 'Login'}
                    </Button>

                    <p className="text-center text-sm text-muted-foreground">
                        Don&apos;t have an account?{" "}
                        <Link
                            href="/signup"
                            className="font-medium text-primary hover:underline"
                        >
                            Signup
                        </Link>
                    </p>
                </form>
            </CardContent>
        </Card>
    )
}

export default LoginPage