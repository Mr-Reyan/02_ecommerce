'use client';

import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { registerSchema } from "@/lib/validations/auth.schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { Register } from "@/services/auth.service";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
export default function RegisterPage() {
    const router = useRouter()
    const {
        register,
        handleSubmit,
        formState: { errors,isSubmitting }
    } = useForm({
        resolver: zodResolver(registerSchema)
    })

    const onSubmit = async(data)=>{
        try {
            const response = await Register(data);
            router.push('/login')
            console.log(response);
        } catch (error) {
            console.log(error);
        }
    }
    

  return (
    <Card className="w-full max-w-md shadow-xl mx-auto mt-25 border-0">
      <CardHeader className="text-center space-y-2">
        <CardTitle className="text-3xl font-bold">
          Create Account
        </CardTitle>

        <CardDescription>
          Get Premium Quality Clothing right away.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form className="space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <div className="space-y-2">
            <Label>Username</Label>

            <Input
            {...register('username')}
            placeholder="john_doe"
            />
            {errors.username && (
            <p className="text-red-500">{errors.username.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Email</Label>

            <Input
            {...register('email')}
            type="email"
            placeholder="you@example.com"
            />
            {errors.email && (
            <p className="text-red-500">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Password</Label>

            <Input
            {...register('password')}
            type="password"
            placeholder="••••••••"
            />
            {errors.password && (
                <p className="text-red-500">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label>Confirm Password</Label>

            <Input
            {...register('confirmPassword')}
              type="password"
              placeholder="••••••••"
            />
            {errors.confirmPassword && (
                <p className="text-red-500">{errors.confirmPassword.message}</p>
            )}
          </div>

          <Button type='submit' className="w-full" disabled={isSubmitting}>
            {isSubmitting? <Loader2 className=" animate-spin" />:'Create Account'}
          </Button>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-primary hover:underline"
            >
              Login
            </Link>
          </p>
        </form>
      </CardContent>
    </Card>
  );
}