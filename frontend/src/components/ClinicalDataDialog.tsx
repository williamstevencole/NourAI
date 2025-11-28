import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { ClinicalData } from '@/types/chat';
import { Trash2 } from 'lucide-react';

interface ClinicalDataDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSave: (data: ClinicalData) => void;
  onDelete?: () => void;
  initialData?: ClinicalData;
}

export function ClinicalDataDialog({
  open,
  onOpenChange,
  onSave,
  onDelete,
  initialData,
}: ClinicalDataDialogProps) {
  const [formData, setFormData] = useState<ClinicalData>(
    initialData || {
      age: undefined,
      gender: undefined,
      weight: undefined,
      height: undefined,
      conditions: [],
      allergies: [],
      medications: [],
      diet_type: undefined,
      activity_level: undefined,
    }
  );

  const [conditionsInput, setConditionsInput] = useState(
    initialData?.conditions?.join(', ') || ''
  );
  const [allergiesInput, setAllergiesInput] = useState(
    initialData?.allergies?.join(', ') || ''
  );
  const [medicationsInput, setMedicationsInput] = useState(
    initialData?.medications?.join(', ') || ''
  );

  const [errors, setErrors] = useState<Record<string, string>>({});

  // Update form when initialData changes
  useEffect(() => {
    if (initialData) {
      setFormData(initialData);
      setConditionsInput(initialData.conditions?.join(', ') || '');
      setAllergiesInput(initialData.allergies?.join(', ') || '');
      setMedicationsInput(initialData.medications?.join(', ') || '');
    }
  }, [initialData]);

  const handleSubmit = () => {
    const newErrors: Record<string, string> = {};

    // Validate age
    if (formData.age !== undefined && (isNaN(formData.age) || formData.age <= 0 || formData.age >= 150)) {
      newErrors.age = 'La edad debe ser un número entre 1 y 149.';
    }

    // Validate weight
    if (formData.weight !== undefined && (isNaN(formData.weight) || formData.weight <= 0)) {
      newErrors.weight = 'El peso debe ser un número mayor a 0.';
    }

    // Validate height
    if (formData.height !== undefined && (isNaN(formData.height) || formData.height <= 0)) {
      newErrors.height = 'La altura debe ser un número mayor a 0.';
    }

    // Validate gender
    const validGenders = ['male', 'female', 'other'];
    if (formData.gender !== undefined && !validGenders.includes(formData.gender)) {
      newErrors.gender = 'Selecciona un sexo válido.';
    }

    // Validate activity_level
    const validActivities = ['sedentary', 'light', 'moderate', 'active', 'very_active'];
    if (formData.activity_level !== undefined && !validActivities.includes(formData.activity_level)) {
      newErrors.activity_level = 'Selecciona un nivel de actividad válido.';
    }

    // Validate diet_type
    const validDiets = ['omnivore', 'vegetarian', 'vegan', 'pescetarian', 'keto', 'other'];
    if (formData.diet_type !== undefined && !validDiets.includes(formData.diet_type)) {
      newErrors.diet_type = 'Selecciona un tipo de dieta válido.';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setErrors({});

    const data: ClinicalData = {
      ...formData,
      conditions: conditionsInput
        .split(',')
        .map((c) => c.trim())
        .filter((c) => c),
      allergies: allergiesInput
        .split(',')
        .map((a) => a.trim())
        .filter((a) => a),
      medications: medicationsInput
        .split(',')
        .map((m) => m.trim())
        .filter((m) => m),
    };
    onSave(data);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Información Clínica</DialogTitle>
          <DialogDescription>
            Para brindarte recomendaciones más personalizadas, cuéntanos un poco sobre ti.
            Esta información se guardará en tu navegador y no será compartida.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="age">Edad</Label>
              <Input
                id="age"
                type="number"
                placeholder="Ej: 30"
                value={formData.age || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseInt(e.target.value) : undefined;
                  setFormData({ ...formData, age: value });
                  if (errors.age) setErrors(prev => ({ ...prev, age: undefined }));
                }}
              />
              {errors.age && <p className="text-red-500 text-sm mt-1">{errors.age}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Sexo</Label>
              <Select
                value={formData.gender}
                onValueChange={(value) => {
                  setFormData({ ...formData, gender: value });
                  if (errors.gender) setErrors(prev => ({ ...prev, gender: undefined }));
                }}
              >
                <SelectTrigger id="gender">
                  <SelectValue placeholder="Selecciona" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Masculino</SelectItem>
                  <SelectItem value="female">Femenino</SelectItem>
                  <SelectItem value="other">Otro</SelectItem>
                </SelectContent>
              </Select>
              {errors.gender && <p className="text-red-500 text-sm mt-1">{errors.gender}</p>}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="weight">Peso (kg)</Label>
              <Input
                id="weight"
                type="number"
                placeholder="Ej: 70"
                value={formData.weight || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseFloat(e.target.value) : undefined;
                  setFormData({ ...formData, weight: value });
                  if (errors.weight) setErrors(prev => ({ ...prev, weight: undefined }));
                }}
              />
              {errors.weight && <p className="text-red-500 text-sm mt-1">{errors.weight}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="height">Altura (cm)</Label>
              <Input
                id="height"
                type="number"
                placeholder="Ej: 170"
                value={formData.height || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseFloat(e.target.value) : undefined;
                  setFormData({ ...formData, height: value });
                  if (errors.height) setErrors(prev => ({ ...prev, height: undefined }));
                }}
              />
              {errors.height && <p className="text-red-500 text-sm mt-1">{errors.height}</p>}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="activity_level">Nivel de actividad física</Label>
            <Select
              value={formData.activity_level}
              onValueChange={(value) => {
                setFormData({ ...formData, activity_level: value });
                if (errors.activity_level) setErrors(prev => ({ ...prev, activity_level: undefined }));
              }}
            >
              <SelectTrigger id="activity_level">
                <SelectValue placeholder="Selecciona tu nivel" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sedentary">Sedentario</SelectItem>
                <SelectItem value="light">Ligera (1-3 días/semana)</SelectItem>
                <SelectItem value="moderate">Moderada (3-5 días/semana)</SelectItem>
                <SelectItem value="active">Activa (6-7 días/semana)</SelectItem>
                <SelectItem value="very_active">Muy activa (atleta)</SelectItem>
              </SelectContent>
            </Select>
            {errors.activity_level && <p className="text-red-500 text-sm mt-1">{errors.activity_level}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="diet_type">Tipo de dieta</Label>
            <Select
              value={formData.diet_type}
              onValueChange={(value) => {
                setFormData({ ...formData, diet_type: value });
                if (errors.diet_type) setErrors(prev => ({ ...prev, diet_type: undefined }));
              }}
            >
              <SelectTrigger id="diet_type">
                <SelectValue placeholder="Selecciona tu dieta" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="omnivore">Omnívora</SelectItem>
                <SelectItem value="vegetarian">Vegetariana</SelectItem>
                <SelectItem value="vegan">Vegana</SelectItem>
                <SelectItem value="pescetarian">Pescetariana</SelectItem>
                <SelectItem value="keto">Cetogénica</SelectItem>
                <SelectItem value="other">Otra</SelectItem>
              </SelectContent>
            </Select>
            {errors.diet_type && <p className="text-red-500 text-sm mt-1">{errors.diet_type}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="conditions">
              Condiciones médicas (separadas por comas)
            </Label>
            <Input
              id="conditions"
              placeholder="Ej: diabetes, hipertensión"
              value={conditionsInput}
              onChange={(e) => setConditionsInput(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="allergies">Alergias (separadas por comas)</Label>
            <Input
              id="allergies"
              placeholder="Ej: nueces, lácteos"
              value={allergiesInput}
              onChange={(e) => setAllergiesInput(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="medications">
              Medicamentos actuales (separados por comas)
            </Label>
            <Input
              id="medications"
              placeholder="Ej: metformina, ibuprofeno"
              value={medicationsInput}
              onChange={(e) => setMedicationsInput(e.target.value)}
            />
          </div>
        </div>

        <DialogFooter className="flex flex-col sm:flex-row sm:justify-between gap-2">
          <div className="flex gap-2">
            {onDelete && initialData && (
              <Button
                variant="destructive"
                onClick={() => {
                  onDelete();
                  onOpenChange(false);
                }}
                className="gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Borrar Datos
              </Button>
            )}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button onClick={handleSubmit}>Guardar</Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
