
import z from "zod"
export const registerSchema = z.object({
    username: z
        .string()
        .trim()
        .min(3, "Username must be at least 3 characters.")
        .max(20, "Username cannot exceed 20 characters.")
        .toLowerCase(),

    email: z
        .email("Please enter a valid email address.")
        .trim()
        .toLowerCase(),

    password: z
        .string()
        .min(6, "Password must be at least 8 characters.")
        .max(20, "Password cannot exceed 20 characters."),
    //  .regex(/[A-Z]/, "Password must contain an uppercase letter.")
    //  .regex(/[a-z]/, "Password must contain a lowercase letter.")
    //  .regex(/[0-9]/, "Password must contain a number.")
    //  .regex(/[^A-Za-z0-9]/, "Password must contain a special character.");
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "Passwords do not match.",
  });

export const loginSchema = z.object({
  username: z
    .string()
    .trim()
    .toLowerCase(),

  password: z
    .string()
    .min(1, "Password is required."),
});


export const emailSchema = z.object({
    email:z.email("Please enter a valid email address.").trim().toLowerCase()
})

export const changePassSchema = z.object({
    password:z.string().min(6,'Password must be at least 6 characters.'),
    confirmPassword:z.string()
})