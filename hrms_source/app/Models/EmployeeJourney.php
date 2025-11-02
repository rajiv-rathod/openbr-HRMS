<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class EmployeeJourney extends Model
{
    use HasFactory;
    protected $table = 'employees_journey';

    public function increments()
    {
        return $this->hasMany(Increment::class, 'employee_id');
    }
    
        public function designation()
    {
        return $this->hasOne('App\Models\Designation', 'id', 'designation_id');
    }
}
