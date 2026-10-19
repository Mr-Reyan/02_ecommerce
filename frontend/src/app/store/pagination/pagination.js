import { Field, FieldLabel } from "@/components/ui/field"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function PaginationBtns({
  prevLink,
  nextLink,
  pageSize = 20,
  onPageSizeChange,
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <Field orientation="horizontal" className="w-fit">
        <FieldLabel htmlFor="select-items-per-page">Items per page</FieldLabel>
        <Select
          value={String(pageSize)}
          onValueChange={(val) => onPageSizeChange && onPageSizeChange(Number(val))}
        >
          <SelectTrigger className="w-20" id="select-items-per-page">
            <SelectValue />
          </SelectTrigger>
          <SelectContent align="start">
            <SelectGroup>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="20">20</SelectItem>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </Field>
      <Pagination className="mx-0 w-auto">
        <PaginationContent>
          <PaginationItem>
            {prevLink ? (
              <PaginationPrevious href={prevLink} />
            ) : (
              <PaginationPrevious className="pointer-events-none opacity-50" />
            )}
          </PaginationItem>
          <PaginationItem>
            {nextLink ? (
              <PaginationNext href={nextLink} />
            ) : (
              <PaginationNext className="pointer-events-none opacity-50" />
            )}
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  )
}
