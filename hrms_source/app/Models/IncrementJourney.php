<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class IncrementJourney extends Model
{
    use HasFactory;
    protected $table = 'increment_journey';
    public function employee()
    {
        return $this->belongsTo(Employee::class, 'employee_id');
    }
}
