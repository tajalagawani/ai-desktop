'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { FileQuestion, Send } from 'lucide-react';
import {
  Field,
  FieldDescription,
  FieldGroup,
  FieldLabel,
  FieldSet,
} from '@/components/ui/field';
import {
  Item,
  ItemContent,
  ItemTitle,
  ItemDescription as ItemDesc,
  ItemMedia,
} from '@/components/ui/item';

interface ParameterField {
  name: string;
  type: 'text' | 'number' | 'email' | 'password' | 'url';
  label: string;
  description?: string;
  required?: boolean;
  defaultValue?: string;
  placeholder?: string;
}

interface ParameterCollectionFormProps {
  title: string;
  description?: string;
  fields: ParameterField[];
  onSubmit: (values: Record<string, string>) => void;
  submitLabel?: string;
}

export function ParameterCollectionForm({
  title,
  description,
  fields,
  onSubmit,
  submitLabel = "Submit"
}: ParameterCollectionFormProps) {
  const [values, setValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    fields.forEach(field => {
      initial[field.name] = field.defaultValue || '';
    });
    return initial;
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(values);
  };

  const isValid = fields.every(field => {
    if (field.required) {
      return values[field.name]?.trim().length > 0;
    }
    return true;
  });

  return (
    <div className="my-3">
      <Item variant="outline" size="default" className="flex-col items-stretch">
        <div className="flex items-start gap-3 mb-3">
          <ItemMedia>
            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
              <FileQuestion className="w-5 h-5 text-blue-600" />
            </div>
          </ItemMedia>
          <ItemContent>
            <ItemTitle className="text-base">{title}</ItemTitle>
            {description && (
              <ItemDesc className="text-sm">{description}</ItemDesc>
            )}
          </ItemContent>
        </div>

        <form onSubmit={handleSubmit}>
          <FieldGroup>
            <FieldSet>
              <FieldGroup>
                {fields.map((field) => (
                  <Field key={field.name}>
                    <FieldLabel htmlFor={field.name}>
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </FieldLabel>
                    <Input
                      id={field.name}
                      name={field.name}
                      type={field.type}
                      placeholder={field.placeholder || field.label}
                      value={values[field.name]}
                      onChange={(e) => setValues({ ...values, [field.name]: e.target.value })}
                      required={field.required}
                    />
                    {field.description && (
                      <FieldDescription>{field.description}</FieldDescription>
                    )}
                  </Field>
                ))}
              </FieldGroup>
            </FieldSet>
            <Field orientation="horizontal">
              <Button type="submit" disabled={!isValid}>
                <Send className="w-4 h-4 mr-2" />
                {submitLabel}
              </Button>
            </Field>
          </FieldGroup>
        </form>
      </Item>
    </div>
  );
}
